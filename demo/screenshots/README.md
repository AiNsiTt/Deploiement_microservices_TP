# Captures d'Écran - Démonstration

## Instructions pour la Démonstration

Pour valider le bon fonctionnement de la plateforme, veuillez prendre les captures d'écran suivantes :

### 1. Services Docker en Cours d'Exécution

**Commande :**
```bash
docker-compose ps
```

**Capture attendue :**
- Tous les services affichent le statut `Up (healthy)`
- Keycloak, NGINX, tous les microservices, bases de données, Redis, Prometheus, Grafana

**Nom du fichier :** `01-docker-compose-ps.png`

---

### 2. Interface Keycloak - Realm Configuration

**URL :** http://localhost:8080

**Étapes :**
1. Se connecter avec admin / admin123
2. Naviguer vers le realm "ecommerce"
3. Afficher la liste des utilisateurs

**Capture attendue :**
- Realm "ecommerce" visible
- Utilisateurs : admin, vendor1, client1

**Nom du fichier :** `02-keycloak-realm.png`

---

### 3. Test API - Authentification Réussie

**Commande :**
```bash
curl -X POST http://localhost:8080/auth/realms/ecommerce/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=client1" \
  -d "password=client123" \
  -d "grant_type=password" \
  -d "client_id=ecommerce-frontend"
```

**Capture attendue :**
- Réponse JSON avec `access_token`, `refresh_token`
- Token type: "Bearer"

**Nom du fichier :** `03-authentication-success.png`

---

### 4. Test API - Liste des Produits

**Commande :**
```bash
curl -X GET http://localhost/api/products \
  -H "Authorization: Bearer <token>"
```

**Capture attendue :**
- Réponse 200 OK
- Liste des produits en JSON

**Nom du fichier :** `04-products-list.png`

---

### 5. Test API - Accès Refusé (Sans Token)

**Commande :**
```bash
curl -X GET http://localhost/api/products
```

**Capture attendue :**
- Réponse 401 Unauthorized
- Message: "Missing authorization header"

**Nom du fichier :** `05-unauthorized-access.png`

---

### 6. Prometheus - Métriques des Services

**URL :** http://localhost:9090

**Étapes :**
1. Accéder à Prometheus
2. Aller dans Status → Targets
3. Afficher tous les services monitorés

**Capture attendue :**
- Tous les services (user-service, product-service, etc.) sont "UP"
- Dernière scrape réussie

**Nom du fichier :** `06-prometheus-targets.png`

---

### 7. Grafana - Dashboard

**URL :** http://localhost:3000

**Étapes :**
1. Se connecter avec admin / admin123
2. Accéder aux dashboards
3. Afficher les métriques

**Capture attendue :**
- Dashboard avec graphiques de métriques
- Services actifs visibles

**Nom du fichier :** `07-grafana-dashboard.png`

---

### 8. Logs d'un Microservice

**Commande :**
```bash
docker-compose logs user-service
```

**Capture attendue :**
- Logs montrant les requêtes traitées
- Validation des tokens
- Actions loguées

**Nom du fichier :** `08-service-logs.png`

---

### 9. Test API - Création de Commande

**Commande :**
```bash
curl -X POST http://localhost/api/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "items": [{"product_id": 1, "quantity": 1, "price": 1499.99}],
    "shipping_address": "123 Rue de la Paix, Paris"
  }'
```

**Capture attendue :**
- Réponse 201 Created
- Commande créée avec statut "confirmed"

**Nom du fichier :** `09-order-creation.png`

---

### 10. NGINX Gateway - Logs d'Accès

**Commande :**
```bash
docker-compose logs nginx
```

**Capture attendue :**
- Logs montrant les requêtes routées
- Rate limiting appliqué
- Headers de sécurité

**Nom du fichier :** `10-nginx-logs.png`

---

## Résumé des Validations

| Capture | Validation |
|---------|------------|
| 01 | ✅ Tous les services sont déployés et healthy |
| 02 | ✅ Keycloak configuré avec realm et utilisateurs |
| 03 | ✅ Authentification fonctionnelle |
| 04 | ✅ API accessible avec token valide |
| 05 | ✅ Sécurité : accès refusé sans token |
| 06 | ✅ Monitoring Prometheus opérationnel |
| 07 | ✅ Dashboards Grafana configurés |
| 08 | ✅ Logs et traçabilité |
| 09 | ✅ Workflow de commande complet |
| 10 | ✅ Gateway NGINX fonctionnel |

---

## Note

Ces captures d'écran démontrent :
- ✅ **Fonctionnalité** : Architecture déployable et testable
- ✅ **Sécurité** : Zero Trust implémenté (authentification, autorisation)
- ✅ **Triade CIA** : Confidentialité (RBAC), Intégrité (validation), Disponibilité (health checks)
- ✅ **Observabilité** : Monitoring et logging centralisés
