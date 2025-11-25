# Scénario de Test 1 : Authentification et Autorisation

## Objectif

Démontrer le fonctionnement du Zero Trust avec authentification Keycloak et autorisation RBAC.

## Prérequis

- Tous les services sont démarrés (`docker-compose up -d`)
- Keycloak est accessible sur http://localhost:8080

## Étape 1 : Authentification en tant que Client

### Requête

```bash
curl -X POST http://localhost:8080/auth/realms/ecommerce/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=client1" \
  -d "password=client123" \
  -d "grant_type=password" \
  -d "client_id=ecommerce-frontend"
```

### Résultat attendu

Réponse JSON contenant :
- `access_token` : JWT token valide
- `refresh_token` : Token de rafraîchissement
- `expires_in` : Durée de validité (300 secondes)
- `token_type` : "Bearer"

### Validation de sécurité

- Le token contient les claims `sub`, `realm_access.roles`, `exp`
- Le rôle "client" est présent dans le token

## Étape 2 : Accès Autorisé (GET /api/products)

### Requête

```bash
TOKEN="<access_token_de_etape_1>"

curl -X GET http://localhost/api/products \
  -H "Authorization: Bearer $TOKEN"
```

### Résultat attendu

Réponse 200 OK avec la liste des produits :

```json
[
  {
    "id": 1,
    "name": "Laptop Dell XPS 15",
    "price": 1499.99,
    "category": "Informatique"
  }
]
```

### Validation de sécurité

- Le JWT est validé par NGINX
- Le JWT est re-validé par le Product Service
- L'accès est autorisé car le rôle "client" peut lire les produits

## Étape 3 : Accès Refusé (POST /api/products)

### Requête

```bash
curl -X POST http://localhost/api/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "description": "Test",
    "price": 99.99,
    "category": "Test",
    "vendor_id": 2,
    "stock_quantity": 10
  }'
```

### Résultat attendu

Réponse 403 Forbidden :

```json
{
  "detail": "Insufficient permissions"
}
```

### Validation de sécurité

- Le rôle "client" ne peut pas créer de produits
- Seuls les rôles "vendor" et "admin" peuvent créer des produits
- Le principe du moindre privilège est respecté

## Étape 4 : Authentification en tant que Vendor

### Requête

```bash
curl -X POST http://localhost:8080/auth/realms/ecommerce/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=vendor1" \
  -d "password=vendor123" \
  -d "grant_type=password" \
  -d "client_id=ecommerce-frontend"
```

### Résultat attendu

Nouveau token avec le rôle "vendor"

## Étape 5 : Accès Autorisé pour Vendor (POST /api/products)

### Requête

```bash
VENDOR_TOKEN="<access_token_vendor>"

curl -X POST http://localhost/api/products \
  -H "Authorization: Bearer $VENDOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nouveau Produit",
    "description": "Créé par vendor",
    "price": 199.99,
    "category": "Test",
    "vendor_id": 2,
    "stock_quantity": 50
  }'
```

### Résultat attendu

Réponse 201 Created avec le produit créé

### Validation de sécurité

- Le rôle "vendor" a les permissions nécessaires
- Le produit est créé avec succès
- L'audit log enregistre l'action

## Étape 6 : Tentative sans Token

### Requête

```bash
curl -X GET http://localhost/api/products
```

### Résultat attendu

Réponse 401 Unauthorized :

```json
{
  "detail": "Missing authorization header"
}
```

### Validation de sécurité

- Aucune requête n'est acceptée sans authentification
- Principe Zero Trust : "Ne jamais faire confiance"

## Conclusion

Ce scénario démontre :

- Authentification forte via Keycloak
- Validation JWT à deux niveaux (Gateway + Service)
- Contrôle d'accès RBAC granulaire
- Principe du moindre privilège
- Principe Zero Trust appliqué

## Métriques de Sécurité

| Critère | Statut |
|---------|--------|
| Authentification obligatoire | Validé |
| Validation JWT | Validé |
| RBAC fonctionnel | Validé |
| Logs d'audit | Validé |
| Chiffrement TLS | Validé (en production) |
