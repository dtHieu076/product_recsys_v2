from sqlalchemy.orm import Session
from sqlalchemy import func, case
from collections import defaultdict
from typing import List, Dict
from datetime import datetime

from app.models.event import Event, EventType
from app.models.product import Product
from app.models.category import Category
from app.schemas.event_schema import EventCreate
from app.schemas.history_schema import ProductHistoryOut, CategoryHistoryOut

def create_event(db: Session, event: EventCreate):
    # Lớp phòng thủ thép: Lấy giá trị và ép thẳng về chữ thường!
    actual_event_type = (
        event.event_type.value if hasattr(event.event_type, 'value') 
        else str(event.event_type).lower()
    )

    db_event = Event(
        event_time=event.event_time,
        event_type=actual_event_type, # Dùng biến đã được "bảo kê" ở đây
        product_id=event.product_id,
        user_id=event.user_id,
        user_session=event.user_session
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_user_history(db: Session, user_id: int) -> List[CategoryHistoryOut]:
    query = (
        db.query(
            Category.category_code.label('category'),
            Product.product_id,
            Product.product_name,
            func.sum(case((Event.event_type == 'view', 1), else_=0)).label('view_count'),
            func.sum(case((Event.event_type == 'cart', 1), else_=0)).label('cart_count'),
            func.sum(case((Event.event_type == 'purchase', 1), else_=0)).label('purchase_count')
        )
        .join(Product, Event.product_id == Product.product_id)
        .join(Category, Product.category_id == Category.category_id, isouter=True)
        .filter(Event.user_id == user_id)
        .filter(Event.event_type.in_(['view', 'cart', 'purchase']))
        .group_by(Category.category_code, Product.product_id, Product.product_name)
        .all()
    )

    categories: Dict[str, Dict] = defaultdict(lambda: {'products': [], 'view': 0, 'cart': 0, 'purchase': 0})

    for row in query:
        category = row.category or 'Uncategorized'
        cat_data = categories[category]
        view_cnt = int(row.view_count or 0)
        cart_cnt = int(row.cart_count or 0)
        purchase_cnt = int(row.purchase_count or 0)
        product_data = {
            'product_id': row.product_id,
            'product_name': row.product_name or 'Unknown Product',
            'view': view_cnt,
            'cart': cart_cnt,
            'purchase': purchase_cnt,
            '_score': purchase_cnt * 100 + cart_cnt * 10 + view_cnt
        }
        cat_data['products'].append(product_data)
        cat_data['view'] += view_cnt
        cat_data['cart'] += cart_cnt
        cat_data['purchase'] += purchase_cnt

    result = []
    for category, cat_data in categories.items():
        cat_data['category'] = category
        # Sort by _score desc, take top 5
        cat_data['products'].sort(key=lambda p: p['_score'], reverse=True)
        top_products_data = cat_data['products'][:5]
        # Clean and convert to Pydantic models
        clean_products = []
        for prod_data in top_products_data:
            clean_prod = dict(prod_data)
            del clean_prod['_score']
            clean_products.append(ProductHistoryOut(**clean_prod))
        cat_data['products'] = clean_products
        result.append(CategoryHistoryOut(**cat_data))

    return result

