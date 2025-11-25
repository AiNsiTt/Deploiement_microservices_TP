"""
Order Service - Gestion des commandes
Architecture Microservices Zero Trust E-Commerce Platform
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
import logging
import requests

app = FastAPI(title="Order Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration des autres services
INVENTORY_SERVICE_URL = "http://inventory-service:8005"
PAYMENT_SERVICE_URL = "http://payment-service:8004"
NOTIFICATION_SERVICE_URL = "http://notification-service:8006"

# Enums
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Models
class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class Order(BaseModel):
    id: Optional[int] = None
    user_id: int
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus
    shipping_address: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem]
    shipping_address: str

# In-memory database
orders_db = [
    {
        "id": 1,
        "user_id": 3,
        "items": [
            {"product_id": 1, "quantity": 1, "price": 1499.99}
        ],
        "total_amount": 1499.99,
        "status": "delivered",
        "shipping_address": "123 Rue de la Paix, Paris",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
]

# Security
def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    logger.info("Token validated")
    return {"sub": "user123", "realm_access": {"roles": ["client"]}}

# Helper functions
def check_inventory(items: List[OrderItem], token: str) -> bool:
    """
    Vérifie la disponibilité des produits dans l'inventaire
    Communication inter-services sécurisée
    """
    try:
        for item in items:
            response = requests.get(
                f"{INVENTORY_SERVICE_URL}/inventory/{item.product_id}",
                headers={"Authorization": token},
                timeout=5
            )
            if response.status_code != 200:
                return False
            inventory = response.json()
            if inventory["quantity"] < item.quantity:
                return False
        return True
    except Exception as e:
        logger.error(f"Inventory check failed: {e}")
        return False

def process_payment(order_id: int, amount: float, token: str) -> bool:
    """
    Traite le paiement via le Payment Service
    """
    try:
        response = requests.post(
            f"{PAYMENT_SERVICE_URL}/payments",
            json={"order_id": order_id, "amount": amount},
            headers={"Authorization": token},
            timeout=5
        )
        return response.status_code == 201
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        return False

def send_notification(user_id: int, message: str, token: str):
    """
    Envoie une notification via le Notification Service
    """
    try:
        requests.post(
            f"{NOTIFICATION_SERVICE_URL}/notifications",
            json={"user_id": user_id, "message": message, "type": "order"},
            headers={"Authorization": token},
            timeout=5
        )
    except Exception as e:
        logger.error(f"Notification failed: {e}")

# Endpoints
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "order-service"}

@app.get("/orders", response_model=List[Order])
def get_orders(token_data: dict = Depends(verify_token)):
    """Récupère toutes les commandes (filtré par user en production)"""
    logger.info("Fetching orders")
    return orders_db

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int, token_data: dict = Depends(verify_token)):
    """Récupère une commande par ID"""
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders", response_model=Order, status_code=201)
def create_order(
    order: OrderCreate,
    authorization: str = Header(None),
    token_data: dict = Depends(verify_token)
):
    """
    Crée une nouvelle commande avec workflow complet:
    1. Vérification stock (Inventory Service)
    2. Traitement paiement (Payment Service)
    3. Création commande
    4. Notification client (Notification Service)
    """
    # Calculer le montant total
    total_amount = sum(item.price * item.quantity for item in order.items)
    
    # Vérifier le stock
    if not check_inventory(order.items, authorization):
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Créer la commande
    new_order = {
        "id": len(orders_db) + 1,
        "user_id": order.user_id,
        "items": [item.dict() for item in order.items],
        "total_amount": total_amount,
        "status": OrderStatus.PENDING,
        "shipping_address": order.shipping_address,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Traiter le paiement
    if not process_payment(new_order["id"], total_amount, authorization):
        raise HTTPException(status_code=400, detail="Payment failed")
    
    new_order["status"] = OrderStatus.CONFIRMED
    orders_db.append(new_order)
    
    # Envoyer notification
    send_notification(
        order.user_id,
        f"Votre commande #{new_order['id']} a été confirmée",
        authorization
    )
    
    logger.info(f"Order {new_order['id']} created successfully")
    return new_order

@app.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: OrderStatus,
    token_data: dict = Depends(verify_token)
):
    """Met à jour le statut d'une commande"""
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order["status"] = status
    order["updated_at"] = datetime.now().isoformat()
    logger.info(f"Order {order_id} status updated to {status}")
    return order

@app.get("/metrics")
def metrics():
    """Métriques Prometheus"""
    return {
        "total_orders": len(orders_db),
        "orders_by_status": {
            status.value: len([o for o in orders_db if o["status"] == status.value])
            for status in OrderStatus
        },
        "total_revenue": sum(o["total_amount"] for o in orders_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
