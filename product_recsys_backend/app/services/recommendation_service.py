import tensorflow as tf
import pickle
import numpy as np
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product_schema import ProductOut
from typing import List
import os
from functools import lru_cache

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
        except Exception as e:
            print(f"ML files not found, using fallback: {e}")

    @classmethod
    def get_recommendations(cls, db: Session, user_id: int) -> List[ProductOut]:
        cls.load_model()
        if cls.model is None:
            # Fallback popular
            popular = db.query(Product).order_by(Product.price.desc()).limit(5).all()
            return [ProductOut.model_validate(p) for p in popular]

        # Get all products
        products = db.query(Product).all()
        prod_ids = [p.product_id for p in products]
        
        try:
            item_indices = cls.item_encoder.transform(prod_ids)
            user_idx = cls.user_encoder.transform([user_id])[0]
            user_inputs = np.array([[user_idx, ii] for ii in item_indices])
            scores = cls.model.predict(user_inputs, verbose=0).flatten()
            top_indices = np.argsort(scores)[-5:][::-1]
            top_prods = [products[i] for i in top_indices]
            return [ProductOut.model_validate(p) for p in top_prods]
        except:
            # Fallback
            return [ProductOut.model_validate(p) for p in products[:5]]

