# Guide de Démarrage Rapide

## Architecture Microservices Zero Trust - E-Commerce Platform
**Auteur:** Quentin Chaillou  
**Date:** Novembre 2025

## Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 8 GB RAM minimum
- Ports disponibles: 80, 443, 3000, 8080, 9090

## Installation en 3 étapes

### 1. Cloner le projet

```bash
git clone <repository-url>
cd SPV_M1_CS_2025_Architecture_Microservice
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env si nécessaire (optionnel pour le développement)
```

### 3. Démarrer la plateforme

```bash
cd infrastructure
docker-compose up -d
```

## Vérification du déploiement

### Vérifier que tous les services sont démarrés

```bash
docker-compose ps
```

Tous les services doivent être dans l'état `Up (healthy)`.

### Accéder aux interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Gateway** | http://localhost | - |
| **Keycloak** | http://localhost:8080 | admin / admin123 |
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | - |

## Tester l'API

### 1. S'authentifier avec Keycloak

```bash
# Obtenir un token pour le client
curl -X POST http://localhost:8080/auth/realms/ecommerce/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=client1" \
  -d "password=client123" \
  -d "grant_type=password" \
  -d "client_id=ecommerce-frontend"
```

Copier le `access_token` de la réponse.

### 2. Tester les endpoints

```bash
# Récupérer les produits
curl -X GET http://localhost/api/products \
  -H "Authorization: Bearer <votre-token>"

# Récupérer le profil utilisateur
curl -X GET http://localhost/api/users/me/profile \
  -H "Authorization: Bearer <votre-token>"

# Créer une commande
curl -X POST http://localhost/api/orders \
  -H "Authorization: Bearer <votre-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "items": [{"product_id": 1, "quantity": 1, "price": 1499.99}],
    "shipping_address": "123 Rue de la Paix, Paris"
  }'
```

## Configuration Keycloak

### Importer le realm (optionnel)

1. Accéder à http://localhost:8080
2. Se connecter avec admin / admin123
3. Cliquer sur "Create Realm"
4. Importer le fichier `infrastructure/keycloak/realm-config.json`

### Utilisateurs de test

| Username | Password | Rôle |
|----------|----------|------|
| admin | admin123 | admin |
| vendor1 | vendor123 | vendor |
| client1 | client123 | client |

## Monitoring

### Grafana Dashboards

1. Accéder à http://localhost:3000
2. Se connecter avec admin / admin123
3. Aller dans Dashboards → Browse
4. Les dashboards sont automatiquement provisionnés

### Prometheus Metrics

Accéder à http://localhost:9090 et exécuter des requêtes:

```promql
# Nombre total d'utilisateurs
sum(user_service_total_users)

# Revenu total
sum(order_service_total_revenue)

# Taux d'erreur HTTP
rate(http_requests_total{status=~"5.."}[5m])
```

## Arrêter la plateforme

```bash
cd infrastructure
docker-compose down
```

Pour supprimer également les volumes (données):

```bash
docker-compose down -v
```

## Logs et Debugging

### Voir les logs d'un service

```bash
docker-compose logs -f user-service
```

### Voir tous les logs

```bash
docker-compose logs -f
```

### Accéder à un conteneur

```bash
docker exec -it user-service sh
```

## Troubleshooting

### Les services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Reconstruire les images
docker-compose build --no-cache

# Redémarrer
docker-compose up -d
```

### Problème de connexion à Keycloak

Attendre 30-60 secondes après le démarrage pour que Keycloak soit complètement initialisé.

```bash
# Vérifier le statut
docker-compose logs keycloak
```

### Port déjà utilisé

Modifier les ports dans `docker-compose.yml` ou arrêter les services utilisant les ports 80, 8080, 3000, 9090.

## Architecture des réseaux Docker

- **frontend**: Communication externe (NGINX, Keycloak)
- **backend**: Communication inter-services (microservices)
- **database**: Isolation des bases de données (principe Zero Trust)

## Prochaines étapes

1. ✅ Explorer l'API avec Postman (collection dans `demo/`)
2. ✅ Consulter les diagrammes d'architecture dans `architecture/`
3. ✅ Lire la documentation complète dans `README.md`
4. ✅ Tester les scénarios de sécurité dans `demo/test-scenarios/`

## Support

Pour toute question, consulter le README.md principal ou les fichiers de documentation dans `security/` et `architecture/`.
