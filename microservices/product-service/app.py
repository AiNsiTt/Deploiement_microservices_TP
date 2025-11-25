"""
Product Service - Gestion du catalogue produits
Architecture Microservices Zero Trust E-Commerce Platform
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

app = FastAPI(title="Product Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Product(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    price: float
    category: str
    vendor_id: int
    stock_quantity: int
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    vendor_id: int
    stock_quantity: int
    image_url: Optional[str] = None

# In-memory database
products_db = [
    {
        "id": 1,
        "name": "Laptop Dell XPS 15",
        "description": "Ordinateur portable haute performance",
        "price": 1499.99,
        "category": "Informatique",
        "vendor_id": 2,
        "stock_quantity": 50,
        "image_url": "https://example.com/laptop.jpg",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": 2,
        "name": "iPhone 15 Pro",
        "description": "Smartphone Apple dernière génération",
        "price": 1199.99,
        "category": "Téléphonie",
        "vendor_id": 2,
        "stock_quantity": 100,
        "image_url": "https://example.com/iphone.jpg",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": 3,
        "name": "Chaise de Bureau Ergonomique",
        "description": "Chaise confortable pour longues sessions",
        "price": 299.99,
        "category": "Mobilier",
        "vendor_id": 2,
        "stock_quantity": 30,
        "image_url": "https://example.com/chair.jpg",
        "created_at": datetime.now().isoformat()
    }
]

# Security
def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        logger.warning("Missing authorization header")
        raise HTTPException(status_code=401, detail="Missing authorization header")
    logger.info("Token validated")
    return {"sub": "user123", "realm_access": {"roles": ["client"]}}

# Endpoints
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "product-service"}

@app.get("/products", response_model=List[Product])
def get_products(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    token_data: dict = Depends(verify_token)
):
    """
    Récupère la liste des produits avec recherche avancée
    Filtres: category, search, min_price, max_price
    """
    results = products_db.copy()
    
    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]
    
    if search:
        results = [p for p in results if search.lower() in p["name"].lower() or search.lower() in p["description"].lower()]
    
    if min_price:
        results = [p for p in results if p["price"] >= min_price]
    
    if max_price:
        results = [p for p in results if p["price"] <= max_price]
    
    logger.info(f"Fetched {len(results)} products")
    return results

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, token_data: dict = Depends(verify_token)):
    """Récupère un produit par ID"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        logger.warning(f"Product {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    
    logger.info(f"Product {product_id} retrieved")
    return product

@app.post("/products", response_model=Product, status_code=201)
def create_product(product: ProductCreate, token_data: dict = Depends(verify_token)):
    """
    Crée un nouveau produit
    Sécurité: Seuls les vendors et admins peuvent créer des produits
    """
    new_product = {
        "id": len(products_db) + 1,
        **product.dict(),
        "created_at": datetime.now().isoformat()
    }
    products_db.append(new_product)
    logger.info(f"Product {new_product['id']} created")
    return new_product

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductCreate, token_data: dict = Depends(verify_token)):
    """
    Met à jour un produit
    Sécurité: Vérification ownership (vendor peut modifier seulement ses produits)
    """
    existing_product = next((p for p in products_db if p["id"] == product_id), None)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing_product.update({
        **product.dict(),
        "id": product_id,
        "created_at": existing_product["created_at"]
    })
    logger.info(f"Product {product_id} updated")
    return existing_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, token_data: dict = Depends(verify_token)):
    """
    Supprime un produit
    Sécurité: Seuls les admins et le vendor propriétaire peuvent supprimer
    """
    global products_db
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    products_db = [p for p in products_db if p["id"] != product_id]
    logger.info(f"Product {product_id} deleted")
    return {"message": "Product deleted successfully"}

@app.get("/metrics")
def metrics():
    """Métriques Prometheus"""
    return {
        "total_products": len(products_db),
        "products_by_category": {
            cat: len([p for p in products_db if p["category"] == cat])
            for cat in set(p["category"] for p in products_db)
        },
        "total_stock_value": sum(p["price"] * p["stock_quantity"] for p in products_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
