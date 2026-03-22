import tensorflow as tf
import pickle
import numpy as np
import os
from functools import lru_cache
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.product import Product
from app.models.event import Event       # Nhớ import thêm Event model
from app.schemas.product_schema import ProductOut

class RecommendationService:
    model = None
    user_encoder = None
    item_encoder = None

    @classmethod
    @lru_cache(maxsize=1)
    def load_model(cls):
        try:
            ml_path = "app/ml"
            cls.model = tf.keras.models.load_model(os.path.join(ml_path, "model.keras"))
            with open(os.path.join(ml_path, "user_encoder.pkl"), "rb") as f:
                cls.user_encoder = pickle.load(f)
            with open(os.path.join(ml_path, "item_encoder.pkl"), "rb") as f:
                cls.item_encoder = pickle.load(f)
            print("Model & Encoders loaded successfully.")
        except Exception as e:
            print(f"ML files not found or error loading, using fallback: {e}")

    @classmethod
    def get_trending_products(cls, db: Session, limit: int = 5) -> List[ProductOut]:
        """
        Hàm Fallback thông minh: Lấy các sản phẩm đang được tương tác nhiều nhất.
        Thực tế hơn rất nhiều so với việc chỉ lấy sản phẩm giá cao.
        """
        trending_query = (
            db.query(Event.product_id, func.count(Event.event_id).label('interaction_count'))
            .group_by(Event.product_id)
            .order_by(func.count(Event.event_id).desc())
            .limit(limit)
            .all()
        )
        
        # Lấy danh sách ID trending
        trending_ids = [row[0] for row in trending_query]
        
        if not trending_ids:
            # Nếu bảng event trống trơn, trả về 5 sản phẩm ngẫu nhiên/đầu tiên từ bảng Product
            fallback_prods = db.query(Product).limit(limit).all()
            return [ProductOut.model_validate(p) for p in fallback_prods]
            
        # Lấy thông tin sản phẩm từ bảng Product
        trending_prods = db.query(Product).filter(Product.product_id.in_(trending_ids)).all()
        
        # Giữ nguyên thứ tự trending
        prod_dict = {p.product_id: p for p in trending_prods}
        ordered_trending = [prod_dict[pid] for pid in trending_ids if pid in prod_dict]
        
        return [ProductOut.model_validate(p) for p in ordered_trending]

    @classmethod
    def get_recommendations(cls, db: Session, user_id: int) -> List[ProductOut]:
        cls.load_model()
        
        # 1. Nếu không có model -> Trả về hàng Hot
        if cls.model is None or cls.user_encoder is None or cls.item_encoder is None:
            return cls.get_trending_products(db)

        try:
            # 2. KIỂM TRA USER MỚI (Cold-start)
            user_idx = cls.user_encoder.transform([user_id])[0]

            # 3. SÀNG LỌC ỨNG VIÊN (SỬA LẠI: Lấy TOÀN BỘ sản phẩm trong kho)
            candidate_prods = db.query(Product.product_id).all()
            candidate_ids = [row[0] for row in candidate_prods]

            # 4. LOẠI TRỪ SẢN PHẨM ĐÃ MUA
            purchased_events = (
                db.query(Event.product_id)
                .filter(Event.user_id == user_id, Event.event_type == 'purchase')
                .all()
            )
            purchased_ids = {row[0] for row in purchased_events} # Dùng set() để tra cứu nhanh
            
            # Lọc bỏ hàng đã mua & kiểm tra xem item có trong model không
            valid_item_classes = set(cls.item_encoder.classes_)
            final_candidate_ids = [
                pid for pid in candidate_ids 
                if pid not in purchased_ids and pid in valid_item_classes
            ]

            # Nếu không có ứng viên nào hợp lệ -> Trả về hàng Hot đại trà
            if not final_candidate_ids:
                return cls.get_trending_products(db)

            # 5. MÔ HÌNH CHẤM ĐIỂM (Ranking)
            item_indices = cls.item_encoder.transform(final_candidate_ids)            
            user_indices = np.array([user_idx] * len(item_indices))
            scores = cls.model.predict([user_indices, item_indices], verbose=0).flatten()

            # 6. LẤY TOP DỰ ĐOÁN TỪ MODEL 
            # Lấy tối đa 5 sản phẩm (có thể ít hơn nếu final_candidate_ids ít)
            num_to_get = min(5, len(scores))
            top_indices = np.argsort(scores)[-num_to_get:][::-1]
            top_product_ids = [final_candidate_ids[i] for i in top_indices]

            # 6.5 CHIẾN THUẬT BACKFILL: NẾU AI CHẤM CHƯA ĐỦ 5 MÓN -> ĐẮP THÊM HÀNG TRENDING VÀO
            if len(top_product_ids) < 5:
                # Loại trừ những món đã mua và những món AI vừa gợi ý
                exclude_ids = purchased_ids.union(set(top_product_ids))
                
                trending_query = (
                    db.query(Event.product_id)
                    .filter(~Event.product_id.in_(exclude_ids)) 
                    .group_by(Event.product_id)
                    .order_by(func.count(Event.event_id).desc())
                    .limit(5 - len(top_product_ids)) # Lấy đúng số lượng còn thiếu
                    .all()
                )
                backfill_ids = [row[0] for row in trending_query]
                top_product_ids.extend(backfill_ids) # Gắn thêm vào đuôi danh sách

            # 7. LẤY DATA TỪ DB VÀ TRẢ VỀ
            top_prods = db.query(Product).filter(Product.product_id.in_(top_product_ids)).all()
            
            # Map lại bằng dictionary để giữ đúng thứ tự (AI suggest trước, Backfill sau)
            prod_dict = {p.product_id: p for p in top_prods}
            ordered_top_prods = [prod_dict[pid] for pid in top_product_ids if pid in prod_dict]

            return [ProductOut.model_validate(p) for p in ordered_top_prods]

        except Exception as e:
            # Bắt mọi lỗi (Cold-start, model error...) -> Xử lý êm ái
            print(f"Prediction logic bypassed for user {user_id}. Reason: {e}")
            return cls.get_trending_products(db)