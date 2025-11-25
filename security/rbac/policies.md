# Politiques RBAC (Role-Based Access Control)

## Architecture Microservices Zero Trust E-Commerce Platform

**Auteur :** Quentin Chaillou  
**Date :** Novembre 2025

---

## Vue d'ensemble

Le système implémente un contrôle d'accès basé sur les rôles (RBAC) avec trois rôles principaux gérés par Keycloak.

## Rôles définis

### 1. Client (client)

**Description :** Utilisateur standard qui achète des produits sur la plateforme.

**Permissions :**

- Autorisé : Consulter le catalogue de produits (GET /api/products)
- Autorisé : Rechercher des produits (GET /api/products?search=...)
- Autorisé : Voir son profil (GET /api/users/me/profile)
- Autorisé : Créer des commandes (POST /api/orders)
- Autorisé : Consulter ses commandes (GET /api/orders)
- Autorisé : Effectuer des paiements (POST /api/payments)
- Autorisé : Recevoir des notifications (GET /api/notifications/user/{id})
- Interdit : Créer/modifier/supprimer des produits
- Interdit : Accéder au dashboard admin
- Interdit : Gérer les stocks

### 2. Vendeur (vendor)

**Description :** Vendeur qui gère son catalogue de produits sur la plateforme.

**Permissions :**

- Toutes les permissions du client
- Autorisé : Créer des produits (POST /api/products)
- Autorisé : Modifier ses produits (PUT /api/products/{id})
- Autorisé : Supprimer ses produits (DELETE /api/products/{id})
- Autorisé : Gérer les stocks de ses produits (PUT /api/inventory/{id})
- Autorisé : Consulter les commandes de ses produits
- Interdit : Modifier les produits d'autres vendeurs
- Interdit : Accéder au dashboard admin complet

### 3. Administrateur (admin)

**Description :** Administrateur système avec accès complet à la plateforme.

**Permissions :**

- Toutes les permissions des clients et vendeurs
- Autorisé : Accéder au dashboard admin (GET /api/admin/*)
- Autorisé : Gérer tous les utilisateurs (POST/PUT/DELETE /api/users)
- Autorisé : Gérer tous les produits
- Autorisé : Gérer tous les stocks
- Autorisé : Consulter toutes les commandes
- Autorisé : Gérer tous les paiements
- Autorisé : Accéder aux métriques système (GET /metrics)
- Autorisé : Consulter les logs et monitoring

## Matrice de permissions

| Endpoint | Client | Vendor | Admin |
|----------|--------|--------|-------|
| GET /api/products | Oui | Oui | Oui |
| POST /api/products | Non | Oui (ses produits) | Oui |
| PUT /api/products/{id} | Non | Oui (ses produits) | Oui |
| DELETE /api/products/{id} | Non | Oui (ses produits) | Oui |
| GET /api/users | Non | Non | Oui |
| GET /api/users/me/profile | Oui | Oui | Oui |
| POST /api/orders | Oui | Oui | Oui |
| GET /api/orders | Oui (ses commandes) | Oui (ses produits) | Oui |
| POST /api/payments | Oui | Oui | Oui |
| GET /api/inventory/{id} | Oui | Oui | Oui |
| PUT /api/inventory/{id} | Non | Oui (ses produits) | Oui |
| GET /api/notifications | Oui (ses notifs) | Oui (ses notifs) | Oui |
| GET /api/admin/* | Non | Non | Oui |
| GET /metrics | Non | Non | Oui |

## Implémentation

### 1. Authentification via Keycloak

Tous les utilisateurs doivent s'authentifier via Keycloak pour obtenir un JWT token contenant leurs rôles.

### 2. Validation au niveau Gateway (NGINX)

Le gateway NGINX valide le JWT token et peut bloquer les requêtes non autorisées avant qu'elles n'atteignent les microservices.

### 3. Validation au niveau Microservice

Chaque microservice vérifie également le JWT token et les rôles pour appliquer le principe de défense en profondeur.

### 4. Vérification de propriété (Ownership)

Pour les ressources appartenant à un utilisateur spécifique (commandes, produits d'un vendeur), le microservice vérifie que l'utilisateur authentifié est bien le propriétaire de la ressource.

## Principe Zero Trust appliqué

### Ne jamais faire confiance, toujours vérifier

Chaque requête est validée, même si elle vient d'un réseau interne. Une double validation est effectuée au niveau du Gateway et du Microservice.

### Moindre privilège

Chaque rôle a uniquement les permissions nécessaires. Aucun accès n'est accordé par défaut.

### Segmentation

Une isolation réseau est mise en place entre les couches (frontend, backend, database). Chaque microservice possède sa propre base de données.

### Audit complet

Toutes les actions sont loguées avec l'identité de l'utilisateur. Une traçabilité complète est assurée pour la conformité.

## Exemple de flux d'autorisation

```
1. Client se connecte → Keycloak
2. Keycloak valide credentials → Retourne JWT avec rôle "client"
3. Client fait une requête GET /api/products → NGINX Gateway
4. NGINX valide JWT → Forward vers Product Service
5. Product Service re-valide JWT → Retourne les produits
6. Client fait une requête POST /api/products → NGINX Gateway
7. NGINX valide JWT et voit rôle "client" → Bloque (403 Forbidden)
```

## Configuration Keycloak

Les rôles sont configurés dans le realm "ecommerce" avec :

- Realm roles : admin, vendor, client
- Client scopes : microservices (contient les claims de rôles)
- Protocol mappers : Inclut les rôles dans le JWT token

## Recommandations de sécurité

1. Utiliser HTTPS/TLS en production
2. Activer MFA (Multi-Factor Authentication) pour les admins
3. Effectuer une rotation régulière des secrets Keycloak
4. Centraliser les audit logs
5. Appliquer un rate limiting par rôle (admins ont des limites plus élevées)
6. Définir un session timeout approprié (15min pour clients, 30min pour admins)
7. Valider strictement les JWT (signature, expiration, issuer)
