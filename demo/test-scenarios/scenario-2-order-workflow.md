# Scénario de Test 2 : Workflow Complet de Commande

## Objectif
Démontrer la communication inter-services sécurisée et le workflow complet d'une commande.

## Flux de la Commande

```
Client → Order Service → Inventory Service (vérification stock)
                      → Payment Service (traitement paiement)
                      → Notification Service (confirmation)
```

## Prérequis
- Authentification en tant que client (voir Scénario 1)
- Token JWT valide

## Étape 1 : Consulter les Produits Disponibles

### Requête
```bash
TOKEN="<access_token>"

curl -X GET http://localhost/api/products \
  -H "Authorization: Bearer $TOKEN"
```

### Résultat attendu
✅ Liste des produits avec leur stock

## Étape 2 : Vérifier le Stock d'un Produit

### Requête
```bash
curl -X GET http://localhost/api/inventory/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Résultat attendu
```json
{
  "product_id": 1,
  "quantity": 50,
  "reserved": 0,
  "available": 50,
  "warehouse_location": "A1"
}
```

## Étape 3 : Créer une Commande

### Requête
```bash
curl -X POST http://localhost/api/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "items": [
      {
        "product_id": 1,
        "quantity": 2,
        "price": 1499.99
      }
    ],
    "shipping_address": "456 Avenue des Champs-Élysées, Paris"
  }'
```

### Workflow Interne (automatique)

1. **Order Service** reçoit la requête
2. **Vérification Stock** : Appel à Inventory Service
   ```
   GET http://inventory-service:8005/inventory/1
   Authorization: Bearer <token>
   ```
3. **Traitement Paiement** : Appel à Payment Service
   ```
   POST http://payment-service:8004/payments
   {
     "order_id": <new_order_id>,
     "amount": 2999.98
   }
   ```
4. **Notification** : Appel à Notification Service
   ```
   POST http://notification-service:8006/notifications
   {
     "user_id": 3,
     "message": "Votre commande #X a été confirmée",
     "type": "order"
   }
   ```

### Résultat attendu
✅ Réponse 201 Created
```json
{
  "id": 2,
  "user_id": 3,
  "items": [...],
  "total_amount": 2999.98,
  "status": "confirmed",
  "shipping_address": "456 Avenue des Champs-Élysées, Paris",
  "created_at": "2025-11-25T12:00:00"
}
```

### Validation de sécurité
- ✅ Chaque appel inter-services propage le JWT token
- ✅ Chaque service valide le token indépendamment
- ✅ Principe de défense en profondeur

## Étape 4 : Vérifier la Notification

### Requête
```bash
curl -X GET http://localhost/api/notifications/user/3 \
  -H "Authorization: Bearer $TOKEN"
```

### Résultat attendu
```json
[
  {
    "id": 1,
    "user_id": 3,
    "type": "order",
    "message": "Votre commande #2 a été confirmée",
    "read": false,
    "sent_at": "2025-11-25T12:00:01"
  }
]
```

## Étape 5 : Consulter le Paiement

### Requête
```bash
curl -X GET http://localhost/api/payments/order/2 \
  -H "Authorization: Bearer $TOKEN"
```

### Résultat attendu
```json
[
  {
    "id": 1,
    "order_id": 2,
    "amount": 2999.98,
    "method": "credit_card",
    "status": "completed",
    "transaction_id": "TXN-000001"
  }
]
```

## Étape 6 : Vérifier la Mise à Jour du Stock

### Requête
```bash
curl -X GET http://localhost/api/inventory/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Résultat attendu
```json
{
  "product_id": 1,
  "quantity": 50,
  "reserved": 2,
  "available": 48,
  "warehouse_location": "A1"
}
```

### Validation
- ✅ Le stock disponible a diminué de 2 unités
- ✅ Les unités sont marquées comme réservées

## Scénario d'Échec : Stock Insuffisant

### Requête
```bash
curl -X POST http://localhost/api/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "items": [
      {
        "product_id": 1,
        "quantity": 100,
        "price": 1499.99
      }
    ],
    "shipping_address": "456 Avenue des Champs-Élysées, Paris"
  }'
```

### Résultat attendu
❌ Réponse 400 Bad Request
```json
{
  "detail": "Insufficient stock"
}
```

### Validation
- ✅ La commande est rejetée avant le paiement
- ✅ Aucune transaction financière n'est effectuée
- ✅ L'intégrité des données est préservée

## Conclusion

Ce scénario démontre :
- ✅ Communication inter-services sécurisée (JWT propagation)
- ✅ Workflow transactionnel complet
- ✅ Gestion des erreurs et rollback
- ✅ Intégrité des données (triade CIA - Intégrité)
- ✅ Traçabilité complète (logs, notifications)

## Diagramme de Séquence

```
Client → API Gateway → Order Service → Inventory Service
                                    → Payment Service
                                    → Notification Service
```

Chaque flèche représente un appel HTTP avec JWT token validé.
