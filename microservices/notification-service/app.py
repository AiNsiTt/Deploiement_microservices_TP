"""
Notification Service - Notifications temps réel
Architecture Microservices Zero Trust E-Commerce Platform
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
import logging

app = FastAPI(title="Notification Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class NotificationType(str, Enum):
    ORDER = "order"
    PAYMENT = "payment"
    SHIPPING = "shipping"
    SYSTEM = "system"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

class Notification(BaseModel):
    id: Optional[int] = None
    user_id: int
    type: NotificationType
    channel: NotificationChannel = NotificationChannel.EMAIL
    message: str
    read: bool = False
    sent_at: Optional[datetime] = None

class NotificationCreate(BaseModel):
    user_id: int
    type: NotificationType
    message: str
    channel: NotificationChannel = NotificationChannel.EMAIL

notifications_db = []

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    return {"sub": "user123"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "notification-service"}

@app.post("/notifications", response_model=Notification, status_code=201)
def create_notification(notification: NotificationCreate, token_data: dict = Depends(verify_token)):
    """
    Envoie une notification
    Canaux: email, SMS, push, in-app
    """
    new_notification = {
        "id": len(notifications_db) + 1,
        **notification.dict(),
        "read": False,
        "sent_at": datetime.now().isoformat()
    }
    
    notifications_db.append(new_notification)
    
    # Simulation d'envoi
    logger.info(f"Notification {new_notification['id']} sent via {notification.channel} to user {notification.user_id}")
    logger.info(f"Message: {notification.message}")
    
    return new_notification

@app.get("/notifications/user/{user_id}", response_model=List[Notification])
def get_user_notifications(user_id: int, token_data: dict = Depends(verify_token)):
    """Récupère les notifications d'un utilisateur"""
    user_notifications = [n for n in notifications_db if n["user_id"] == user_id]
    return user_notifications

@app.put("/notifications/{notification_id}/read")
def mark_as_read(notification_id: int, token_data: dict = Depends(verify_token)):
    """Marque une notification comme lue"""
    notification = next((n for n in notifications_db if n["id"] == notification_id), None)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification["read"] = True
    logger.info(f"Notification {notification_id} marked as read")
    return notification

@app.get("/metrics")
def metrics():
    return {
        "total_notifications": len(notifications_db),
        "notifications_by_type": {
            ntype.value: len([n for n in notifications_db if n["type"] == ntype.value])
            for ntype in NotificationType
        },
        "notifications_by_channel": {
            channel.value: len([n for n in notifications_db if n["channel"] == channel.value])
            for channel in NotificationChannel
        },
        "unread_notifications": len([n for n in notifications_db if not n["read"]])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
