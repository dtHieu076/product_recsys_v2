import tensorflow as tf
import pickle
import numpy as np
import os
from functools import lru_cache
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.product import Product
from app.models.event import Event
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
        """
        trending_query = (
            db.query(Event.product_id, func.count(Event.event_id).label('interaction_count'))
            .group_by(Event.product_id)
            .order_by(func.count(Event.event_id).desc())
            .limit(limit)
            .all()
        )
        
        trending_ids = [row[0] for row in trending_query]
        
        if not trending_ids:
            # Fallback nếu bảng Event trống
            fallback_prods = db.query(Product).limit(limit).all()
            for p in fallback_prods:
                p.confidence_score = 0.5 # Gắn thẳng thuộc tính động
            return [ProductOut.model_validate(p) for p in fallback_prods]
            
        # Lấy thông tin sản phẩm từ bảng Product
        trending_prods = db.query(Product).filter(Product.product_id.in_(trending_ids)).all()
        
        # Giữ nguyên thứ tự trending
        prod_dict = {p.product_id: p for p in trending_prods}
        ordered_trending = [prod_dict[pid] for pid in trending_ids if pid in prod_dict]
        
        # Gắn confidence_score cho hàng trending
        for p in ordered_trending:
            p.confidence_score = 0.55
            
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

            # 3. SÀNG LỌC ỨNG VIÊN (Lấy toàn bộ, KHÔNG loại trừ hàng đã mua)
            candidate_prods = db.query(Product.product_id).all()
            candidate_ids = [row[0] for row in candidate_prods]
            
            # Chỉ cần kiểm tra xem item có nằm trong tập model đã học không
            valid_item_classes = set(cls.item_encoder.classes_)
            final_candidate_ids = [
                pid for pid in candidate_ids 
                if pid in valid_item_classes
            ]

            # Nếu không có ứng viên nào hợp lệ -> Trả về hàng Hot đại trà
            if not final_candidate_ids:
                return cls.get_trending_products(db)

            # 4. MÔ HÌNH CHẤM ĐIỂM (Ranking)
            item_indices = cls.item_encoder.transform(final_candidate_ids)            
            user_indices = np.array([user_idx] * len(item_indices))
            scores = cls.model.predict([user_indices, item_indices], verbose=0).flatten()
            
            # Normalize scores to confidence (0.7-1.0 range for AI predictions)
            if len(scores) > 0:
                scores_min, scores_max = scores.min(), scores.max()
                # Tránh chia cho 0 nếu min == max
                if scores_max > scores_min:
                    confidence_scores = (scores - scores_min) / (scores_max - scores_min) * 0.3 + 0.7
                else:
                    confidence_scores = 0.85 * np.ones_like(scores)
            else:
                confidence_scores = np.array([])

            # 5. LẤY TOP DỰ ĐOÁN TỪ MODEL 
            num_to_get = min(5, len(scores))
            top_indices = np.argsort(scores)[-num_to_get:][::-1]
            
            top_product_ids = [final_candidate_ids[i] for i in top_indices]
            ai_conf_scores = [confidence_scores[i] for i in top_indices]

            # 6. CHIẾN THUẬT BACKFILL (Nếu AI chấm chưa đủ 5 món)
            if len(top_product_ids) < 5:
                # Chỉ loại trừ những món AI VỪA gợi ý (để tránh trùng lặp trong list trả về)
                exclude_ids = set(top_product_ids)
                
                trending_query = (
                    db.query(Event.product_id, func.count(Event.event_id).label('interaction_count'))
                    .filter(~Event.product_id.in_(exclude_ids)) 
                    .group_by(Event.product_id)
                    .order_by(func.count(Event.event_id).desc())
                    .limit(5 - len(top_product_ids))
                    .all()
                )
                
                backfill_ids = [row[0] for row in trending_query]
                
                # Compute backfill confidence based on interaction count (0.4-0.7)
                backfill_counts = [row[1] for row in trending_query]
                max_count = max(backfill_counts) if backfill_counts else 1
                backfill_conf_scores = [(count / max_count) * 0.3 + 0.4 for count in backfill_counts]
                
                top_product_ids.extend(backfill_ids)

            # 7. LẤY DATA TỪ DB VÀ TRẢ VỀ CÙNG CONFIDENCE SCORE
            top_prods = db.query(Product).filter(Product.product_id.in_(top_product_ids)).all()
            
            # Map lại bằng dictionary để giữ đúng thứ tự (AI suggest trước, Backfill sau)
            prod_dict = {p.product_id: p for p in top_prods}
            
            conf_idx = 0
            result_prods = []
            
            for pid in top_product_ids:
                if pid in prod_dict:
                    p = prod_dict[pid] # p là object của SQLAlchemy
                    
                    if conf_idx < len(ai_conf_scores):
                        conf_score = ai_conf_scores[conf_idx]
                        conf_idx += 1
                    elif conf_idx - len(ai_conf_scores) < len(backfill_conf_scores):
                        conf_score = backfill_conf_scores[conf_idx - len(ai_conf_scores)]
                        conf_idx += 1
                    else:
                        conf_score = 0.5  # fallback an toàn
                        
                    # Sử dụng thuộc tính động: Gán trực tiếp điểm vào object
                    p.confidence_score = round(float(conf_score), 4)
                    
                    # model_validate sẽ tự động đọc p.confidence_score và các trường khác
                    result_prods.append(ProductOut.model_validate(p))
                    
            return result_prods

        except Exception as e:
            import traceback
            traceback.print_exc() # In chi tiết lỗi ra terminal để dễ debug hơn
            print(f"Prediction logic bypassed for user {user_id}. Reason: {e}")
            return cls.get_trending_products(db)