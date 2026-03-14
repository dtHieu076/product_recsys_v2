from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.product_api import router as product_router
from app.api.event_api import router as event_router
from app.api.recommendation_api import router as recommendation_router
from app.api.auth_api import router as auth_router
from app.config.database import engine
from app.models.user import Base
from app.models.category import Category
from app.models.product import Product
from app.models.event import Event

app = FastAPI(title="Product RecSys Backend", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(event_router)
app.include_router(recommendation_router)
app.include_router(auth_router)

# Create tables if not exist (dev only)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Product Recommendation System Backend is running!"}

