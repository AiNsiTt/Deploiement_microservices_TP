# Guide de Dépannage

## Architecture Microservices Zero Trust - E-Commerce Platform

Ce guide vous aide à résoudre les problèmes courants rencontrés lors du déploiement et de l'utilisation de la plateforme.

---

## Problème 1 : Erreur "Not Found" lors de l'appel à l'API

### Symptôme
```bash
curl -X GET http://localhost/api/products -H "Authorization: Bearer $TOKEN"
{"detail":"Not Found"}
```

### Causes possibles

1. **Les microservices ne sont pas démarrés**
2. **NGINX ne route pas correctement**
3. **Les réseaux Docker ne sont pas configurés**

### Solution

#### Étape 1 : Vérifier que tous les services sont démarrés

```bash
cd infrastructure
docker-compose ps
```

Tous les services doivent afficher le statut "Up" ou "Up (healthy)".

#### Étape 2 : Vérifier les logs de NGINX

```bash
docker-compose logs nginx
```

Recherchez les erreurs de type "connection refused" ou "upstream not found".

#### Étape 3 : Tester directement les microservices

```bash
# Tester le Product Service directement
curl http://localhost:8002/api/products

# Si cela fonctionne, le problème vient de NGINX
```

#### Étape 4 : Redémarrer NGINX

```bash
docker-compose restart nginx
```

#### Étape 5 : Reconstruire et redémarrer tous les services

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Problème 2 : Impossible d'obtenir un token Keycloak

### Symptôme
```bash
curl -X POST http://localhost:8080/auth/realms/ecommerce/protocol/openid-connect/token ...
{"error":"Unable to find matching target resource method"}
```

### Cause
L'URL Keycloak a changé dans la version 23+.

### Solution

Utiliser `/realms` au lieu de `/auth/realms` :

```bash
curl -X POST http://localhost:8080/realms/ecommerce/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=client1" \
  -d "password=client123" \
  -d "grant_type=password" \
  -d "client_id=ecommerce-frontend"
```

Si cela ne fonctionne toujours pas, suivre le guide de configuration manuelle dans `infrastructure/keycloak/CONFIGURATION.md`.

---

## Problème 3 : Erreur "Invalid user credentials"

### Symptôme
```json
{"error":"invalid_grant","error_description":"Invalid user credentials"}
```

### Causes possibles

1. Le mot de passe est incorrect
2. L'utilisateur n'existe pas
3. L'utilisateur est désactivé

### Solution

1. Accéder à Keycloak : http://localhost:8080
2. Se connecter avec admin / admin123
3. Aller dans Users → Rechercher l'utilisateur
4. Vérifier que "Enabled" est ON
5. Aller dans Credentials → Réinitialiser le mot de passe
6. S'assurer que "Temporary" est OFF

---

## Problème 4 : Erreur 403 Forbidden

### Symptôme
```json
{"detail":"Insufficient permissions"}
```

### Cause
L'utilisateur n'a pas les permissions nécessaires pour effectuer cette action.

### Solution

Vérifier les rôles de l'utilisateur :

1. Accéder à Keycloak
2. Aller dans Users → Sélectionner l'utilisateur
3. Aller dans Role mapping
4. Vérifier que le bon rôle est assigné (client, vendor, admin)

Consulter la matrice de permissions dans `security/rbac/policies.md`.

---

## Problème 5 : Les conteneurs ne démarrent pas

### Symptôme
```bash
docker-compose ps
# Certains services affichent "Exit 1" ou "Restarting"
```

### Solution

#### Vérifier les logs du service défaillant

```bash
docker-compose logs <nom-du-service>
```

#### Problèmes courants

**Port déjà utilisé :**
```bash
# Trouver le processus utilisant le port
sudo lsof -i :8080
# Ou modifier le port dans docker-compose.yml
```

**Manque de mémoire :**
```bash
# Vérifier l'utilisation de la mémoire
docker stats
# Augmenter la mémoire allouée à Docker
```

**Erreur de dépendances Python :**
```bash
# Reconstruire l'image
docker-compose build --no-cache <nom-du-service>
```

---

## Problème 6 : Keycloak ne démarre pas

### Symptôme
```bash
docker-compose logs keycloak
# Erreurs de base de données ou timeout
```

### Solution

Keycloak nécessite 30 à 60 secondes pour démarrer complètement.

```bash
# Attendre que Keycloak soit prêt
docker-compose logs -f keycloak

# Rechercher le message "Keycloak ... started"
```

Si Keycloak ne démarre toujours pas :

```bash
# Supprimer les volumes et redémarrer
docker-compose down -v
docker-compose up -d keycloak
```

---

## Problème 7 : Erreur de connexion entre services

### Symptôme
Les microservices ne peuvent pas communiquer entre eux.

### Cause
Problème de réseau Docker.

### Solution

```bash
# Vérifier les réseaux Docker
docker network ls

# Inspecter le réseau backend
docker network inspect deploiement_microservices_tp_backend

# Recréer les réseaux
docker-compose down
docker-compose up -d
```

---

## Problème 8 : Rate Limiting (429 Too Many Requests)

### Symptôme
```json
{"detail":"Too Many Requests"}
```

### Cause
Vous avez dépassé la limite de requêtes par seconde (10 req/s).

### Solution

Attendre quelques secondes avant de réessayer, ou modifier la configuration NGINX dans `gateway/nginx/nginx.conf` :

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=20r/s;
```

---

## Script de Diagnostic Automatique

Un script de diagnostic est disponible pour vérifier l'état de tous les services :

```bash
cd infrastructure
./check-services.sh
```

Ce script vérifie :
- L'état des conteneurs Docker
- La connectivité des microservices
- Le fonctionnement de l'API Gateway
- Les routes NGINX

---

## Commandes Utiles

### Redémarrer tous les services
```bash
cd infrastructure
docker-compose restart
```

### Voir les logs en temps réel
```bash
docker-compose logs -f
```

### Voir les logs d'un service spécifique
```bash
docker-compose logs -f product-service
```

### Accéder au shell d'un conteneur
```bash
docker exec -it product-service sh
```

### Nettoyer complètement
```bash
docker-compose down -v
docker system prune -a
```

### Reconstruire tout
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## Besoin d'aide supplémentaire ?

1. Consulter le README.md principal
2. Consulter le guide QUICKSTART.md
3. Consulter la documentation Keycloak : `infrastructure/keycloak/CONFIGURATION.md`
4. Vérifier les logs détaillés de chaque service
5. Exécuter le script de diagnostic : `./check-services.sh`
