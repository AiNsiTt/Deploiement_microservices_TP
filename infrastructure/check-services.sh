#!/bin/bash

echo "=========================================="
echo "Diagnostic des Services - E-Commerce Platform"
echo "=========================================="
echo ""

echo "1. Vérification des conteneurs Docker..."
echo "------------------------------------------"
docker-compose ps
echo ""

echo "2. Test de connectivité des microservices..."
echo "------------------------------------------"

services=(
    "user-service:8001"
    "product-service:8002"
    "order-service:8003"
    "payment-service:8004"
    "inventory-service:8005"
    "notification-service:8006"
    "admin-dashboard:8007"
)

for service in "${services[@]}"; do
    name="${service%%:*}"
    port="${service##*:}"
    echo -n "Testing $name on port $port... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "OK (HTTP $response)"
    else
        echo "FAILED (HTTP $response)"
    fi
done

echo ""
echo "3. Test de l'API Gateway NGINX..."
echo "------------------------------------------"
echo -n "Testing NGINX on port 80... "
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
echo "HTTP $response"

echo ""
echo "4. Test des routes NGINX..."
echo "------------------------------------------"

routes=(
    "/api/products"
    "/api/users"
    "/api/orders"
)

for route in "${routes[@]}"; do
    echo -n "Testing route $route... "
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost$route 2>/dev/null)
    echo "HTTP $response"
done

echo ""
echo "5. Logs récents de NGINX..."
echo "------------------------------------------"
docker-compose logs --tail=20 nginx

echo ""
echo "=========================================="
echo "Diagnostic terminé"
echo "=========================================="
