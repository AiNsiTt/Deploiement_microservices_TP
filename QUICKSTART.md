# Guide de Démarrage Rapide

## Architecture Microservices Zero Trust - E-Commerce Platform

**Auteur :** Quentin Chaillou  
**Date :** Novembre 2025  
**Module :** Architecture Microservices & Sécurité

---

## Prérequis

Avant de démarrer la plateforme, assurez-vous que les éléments suivants sont installés sur votre système :

- Docker version 20.10 ou supérieure
- Docker Compose version 2.0 ou supérieure
- 8 GB de RAM minimum disponible
- Les ports suivants doivent être disponibles : 80, 443, 3000, 8080, 9090

## Installation en 3 étapes

### Étape 1 : Cloner le projet

```bash
git clone https://github.com/AiNsiTt/Deploiement_microservices_TP.git
cd Deploiement_microservices_TP
```

### Étape 2 : Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer le fichier .env si nécessaire (optionnel pour le développement)
```

### Étape 3 : Démarrer la plateforme

```bash
cd infrastructure
docker-compose up -d
```

## Vérification du déploiement

### Vérifier que tous les services sont démarrés

```bash
docker-compose ps
```

Tous les services doivent afficher l'état "Up (healthy)".

### Accéder aux interfaces

| Service | URL | Identifiants |
|---------|-----|-------------|
| API Gateway | http://localhost | - |
| Keycloak | http://localhost:8080 | admin / admin123 |
| Grafana | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | - |

## Tester l'API

### Authentification avec Keycloak

Pour obtenir un token d'accès, exécutez la commande suivante :

```bash
curl -X POST http://localhost:8080/auth/realms/ecommerce/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=client1" \
  -d "password=client123" \
  -d "grant_type=password" \
  -d "client_id=ecommerce-frontend"
```

Copiez la valeur du champ `access_token` de la réponse pour l'utiliser dans les requêtes suivantes.

### Tester les endpoints

#### Récupérer la liste des produits

```bash
curl -X GET http://localhost/api/products \
  -H "Authorization: Bearer <votre-token>"
```

#### Récupérer le profil utilisateur

```bash
curl -X GET http://localhost/api/users/me/profile \
  -H "Authorization: Bearer <votre-token>"
```

#### Créer une commande

```bash
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

Si le realm n'est pas automatiquement configuré, vous pouvez l'importer manuellement :

1. Accéder à http://localhost:8080
2. Se connecter avec les identifiants admin / admin123
3. Cliquer sur "Create Realm"
4. Importer le fichier `infrastructure/keycloak/realm-config.json`

### Utilisateurs de test

Les utilisateurs suivants sont préconfigurés pour les tests :

| Nom d'utilisateur | Mot de passe | Rôle |
|----------|----------|------|
| admin | admin123 | admin |
| vendor1 | vendor123 | vendor |
| client1 | client123 | client |

## Monitoring

### Accéder à Grafana

1. Accéder à http://localhost:3000
2. Se connecter avec les identifiants admin / admin123
3. Naviguer vers Dashboards → Browse
4. Les dashboards sont automatiquement provisionnés

### Consulter les métriques Prometheus

Accéder à http://localhost:9090 et exécuter des requêtes PromQL, par exemple :

```promql
# Nombre total d'utilisateurs
sum(user_service_total_users)

# Revenu total
sum(order_service_total_revenue)

# Taux d'erreur HTTP
rate(http_requests_total{status=~"5.."}[5m])
```

## Arrêter la plateforme

Pour arrêter tous les services :

```bash
cd infrastructure
docker-compose down
```

Pour supprimer également les volumes (données) :

```bash
docker-compose down -v
```

## Logs et Debugging

### Consulter les logs d'un service

```bash
docker-compose logs -f user-service
```

### Consulter tous les logs

```bash
docker-compose logs -f
```

### Accéder à un conteneur

```bash
docker exec -it user-service sh
```

## Résolution de problèmes

### Les services ne démarrent pas

Vérifier les logs pour identifier l'erreur :

```bash
docker-compose logs
```

Reconstruire les images si nécessaire :

```bash
docker-compose build --no-cache
docker-compose up -d
```

### Problème de connexion à Keycloak

Keycloak nécessite 30 à 60 secondes pour être complètement initialisé après le démarrage. Vérifier le statut :

```bash
docker-compose logs keycloak
```

### Port déjà utilisé

Si un port est déjà utilisé, modifier les ports dans le fichier `docker-compose.yml` ou arrêter les services utilisant les ports 80, 8080, 3000, 9090.

## Architecture des réseaux Docker

L'architecture utilise trois réseaux Docker distincts pour assurer la sécurité :

- **frontend** : Communication externe (clients vers gateway)
- **backend** : Communication inter-services (microservices)
- **database** : Isolation des bases de données (principe Zero Trust)

## Prochaines étapes

1. Explorer l'API avec les commandes curl ou Postman
2. Consulter les diagrammes d'architecture dans le dossier `architecture/`
3. Lire la documentation complète dans `README.md`
4. Tester les scénarios de sécurité dans `demo/test-scenarios/`

## Support

Pour toute question, consulter le README.md principal ou les fichiers de documentation dans les dossiers `security/` et `architecture/`.
