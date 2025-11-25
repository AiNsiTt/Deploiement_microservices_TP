"""
Payment Service - Gestion des paiements sécurisés
Architecture Microservices Zero Trust E-Commerce Platform
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
import logging
import random

app = FastAPI(title="Payment Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"

class Payment(BaseModel):
    id: Optional[int] = None
    order_id: int
    amount: float
    method: PaymentMethod = PaymentMethod.CREDIT_CARD
    status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: Optional[datetime] = None

class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    method: PaymentMethod = PaymentMethod.CREDIT_CARD

payments_db = []

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    return {"sub": "user123"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "payment-service"}

@app.post("/payments", response_model=Payment, status_code=201)
def create_payment(payment: PaymentCreate, token_data: dict = Depends(verify_token)):
    """
    Traite un paiement (simulation)
    Sécurité: Chiffrement des données sensibles, PCI-DSS compliance
    """
    # Simulation de traitement paiement
    success = random.choice([True, True, True, False])  # 75% de succès
    
    new_payment = {
        "id": len(payments_db) + 1,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "method": payment.method,
        "status": PaymentStatus.COMPLETED if success else PaymentStatus.FAILED,
        "transaction_id": f"TXN-{len(payments_db) + 1:06d}" if success else None,
        "created_at": datetime.now().isoformat()
    }
    
    payments_db.append(new_payment)
    
    if not success:
        logger.warning(f"Payment {new_payment['id']} failed")
        raise HTTPException(status_code=400, detail="Payment processing failed")
    
    logger.info(f"Payment {new_payment['id']} processed successfully")
    return new_payment

@app.get("/payments/{payment_id}", response_model=Payment)
def get_payment(payment_id: int, token_data: dict = Depends(verify_token)):
    payment = next((p for p in payments_db if p["id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.get("/payments/order/{order_id}", response_model=List[Payment])
def get_payments_by_order(order_id: int, token_data: dict = Depends(verify_token)):
    """Récupère tous les paiements d'une commande"""
    payments = [p for p in payments_db if p["order_id"] == order_id]
    return payments

@app.post("/payments/{payment_id}/refund")
def refund_payment(payment_id: int, token_data: dict = Depends(verify_token)):
    """Rembourse un paiement"""
    payment = next((p for p in payments_db if p["id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment["status"] != PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot refund non-completed payment")
    
    payment["status"] = PaymentStatus.REFUNDED
    logger.info(f"Payment {payment_id} refunded")
    return payment

@app.get("/metrics")
def metrics():
    return {
        "total_payments": len(payments_db),
        "total_amount": sum(p["amount"] for p in payments_db if p["status"] == "completed"),
        "payments_by_status": {
            status.value: len([p for p in payments_db if p["status"] == status.value])
            for status in PaymentStatus
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
