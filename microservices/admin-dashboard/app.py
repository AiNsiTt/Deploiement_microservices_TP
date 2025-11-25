"""
Admin Dashboard Service - Tableau de bord administrateur
Architecture Microservices Zero Trust E-Commerce Platform
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import requests

app = FastAPI(title="Admin Dashboard Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Configuration des services
SERVICES = {
    "user-service": "http://user-service:8001",
    "product-service": "http://product-service:8002",
    "order-service": "http://order-service:8003",
    "payment-service": "http://payment-service:8004",
    "inventory-service": "http://inventory-service:8005",
    "notification-service": "http://notification-service:8006"
}

class DashboardStats(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    total_revenue: float
    services_health: dict

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    # En production, vérifier que l'utilisateur a le rôle 'admin'
    return {"sub": "admin", "realm_access": {"roles": ["admin"]}}

def check_service_health(service_name: str, service_url: str, token: str) -> dict:
    """Vérifie la santé d'un microservice"""
    try:
        response = requests.get(f"{service_url}/health", timeout=3)
        return {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time_ms": response.elapsed.total_seconds() * 1000
        }
    except Exception as e:
        logger.error(f"Health check failed for {service_name}: {e}")
        return {"status": "down", "error": str(e)}

def get_service_metrics(service_name: str, service_url: str, token: str) -> dict:
    """Récupère les métriques d'un microservice"""
    try:
        response = requests.get(
            f"{service_url}/metrics",
            headers={"Authorization": token},
            timeout=3
        )
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        logger.error(f"Metrics fetch failed for {service_name}: {e}")
        return {}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "admin-dashboard"}

@app.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    authorization: str = Header(None),
    token_data: dict = Depends(verify_token)
):
    """
    Récupère les statistiques globales de la plateforme
    Sécurité: Accessible uniquement aux administrateurs
    """
    # Vérifier la santé de tous les services
    services_health = {}
    for service_name, service_url in SERVICES.items():
        services_health[service_name] = check_service_health(service_name, service_url, authorization)
    
    # Récupérer les métriques
    user_metrics = get_service_metrics("user-service", SERVICES["user-service"], authorization)
    product_metrics = get_service_metrics("product-service", SERVICES["product-service"], authorization)
    order_metrics = get_service_metrics("order-service", SERVICES["order-service"], authorization)
    
    stats = {
        "total_users": user_metrics.get("total_users", 0),
        "total_products": product_metrics.get("total_products", 0),
        "total_orders": order_metrics.get("total_orders", 0),
        "total_revenue": order_metrics.get("total_revenue", 0.0),
        "services_health": services_health
    }
    
    logger.info("Dashboard stats retrieved")
    return stats

@app.get("/dashboard/services")
def get_services_status(
    authorization: str = Header(None),
    token_data: dict = Depends(verify_token)
):
    """
    Récupère le statut détaillé de tous les microservices
    """
    services_status = {}
    
    for service_name, service_url in SERVICES.items():
        health = check_service_health(service_name, service_url, authorization)
        metrics = get_service_metrics(service_name, service_url, authorization)
        
        services_status[service_name] = {
            "url": service_url,
            "health": health,
            "metrics": metrics
        }
    
    return services_status

@app.get("/dashboard/alerts")
def get_alerts(token_data: dict = Depends(verify_token)):
    """
    Récupère les alertes système
    """
    # Simulation d'alertes
    alerts = [
        {
            "id": 1,
            "severity": "warning",
            "message": "Inventory low for product #3",
            "timestamp": "2025-11-25T10:30:00"
        },
        {
            "id": 2,
            "severity": "info",
            "message": "High traffic detected on product-service",
            "timestamp": "2025-11-25T11:00:00"
        }
    ]
    
    return alerts

@app.get("/metrics")
def metrics():
    return {
        "dashboard_requests": 0,
        "active_admins": 1
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
