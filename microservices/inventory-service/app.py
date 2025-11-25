"""
Inventory Service - Gestion des stocks
Architecture Microservices Zero Trust E-Commerce Platform
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

app = FastAPI(title="Inventory Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class Inventory(BaseModel):
    product_id: int
    quantity: int
    reserved: int = 0
    available: int
    warehouse_location: str
    last_updated: Optional[datetime] = None

class InventoryUpdate(BaseModel):
    quantity: int

inventory_db = [
    {"product_id": 1, "quantity": 50, "reserved": 0, "available": 50, "warehouse_location": "A1", "last_updated": datetime.now().isoformat()},
    {"product_id": 2, "quantity": 100, "reserved": 0, "available": 100, "warehouse_location": "A2", "last_updated": datetime.now().isoformat()},
    {"product_id": 3, "quantity": 30, "reserved": 0, "available": 30, "warehouse_location": "B1", "last_updated": datetime.now().isoformat()},
]

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    return {"sub": "user123"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "inventory-service"}

@app.get("/inventory/{product_id}", response_model=Inventory)
def get_inventory(product_id: int, token_data: dict = Depends(verify_token)):
    """Récupère le stock d'un produit"""
    inventory = next((i for i in inventory_db if i["product_id"] == product_id), None)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

@app.put("/inventory/{product_id}", response_model=Inventory)
def update_inventory(product_id: int, update: InventoryUpdate, token_data: dict = Depends(verify_token)):
    """Met à jour le stock d'un produit"""
    inventory = next((i for i in inventory_db if i["product_id"] == product_id), None)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    inventory["quantity"] = update.quantity
    inventory["available"] = update.quantity - inventory["reserved"]
    inventory["last_updated"] = datetime.now().isoformat()
    logger.info(f"Inventory for product {product_id} updated to {update.quantity}")
    return inventory

@app.post("/inventory/{product_id}/reserve")
def reserve_inventory(product_id: int, quantity: int, token_data: dict = Depends(verify_token)):
    """Réserve du stock pour une commande"""
    inventory = next((i for i in inventory_db if i["product_id"] == product_id), None)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    if inventory["available"] < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    inventory["reserved"] += quantity
    inventory["available"] -= quantity
    inventory["last_updated"] = datetime.now().isoformat()
    logger.info(f"Reserved {quantity} units of product {product_id}")
    return inventory

@app.get("/metrics")
def metrics():
    return {
        "total_products": len(inventory_db),
        "total_quantity": sum(i["quantity"] for i in inventory_db),
        "total_reserved": sum(i["reserved"] for i in inventory_db),
        "total_available": sum(i["available"] for i in inventory_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
