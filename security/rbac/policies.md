# Politiques RBAC (Role-Based Access Control)

## Architecture Microservices Zero Trust E-Commerce Platform
**Auteur:** Quentin Chaillou  
**Date:** Novembre 2025

## Vue d'ensemble

Le système implémente un contrôle d'accès basé sur les rôles (RBAC) avec trois rôles principaux gérés par Keycloak.

## Rôles définis

### 1. Client (client)
**Description:** Utilisateur standard qui achète des produits sur la plateforme.

**Permissions:**
- ✅ Consulter le catalogue de produits (GET /api/products)
- ✅ Rechercher des produits (GET /api/products?search=...)
- ✅ Voir son profil (GET /api/users/me/profile)
- ✅ Créer des commandes (POST /api/orders)
- ✅ Consulter ses commandes (GET /api/orders)
- ✅ Effectuer des paiements (POST /api/payments)
- ✅ Recevoir des notifications (GET /api/notifications/user/{id})
- ❌ Créer/modifier/supprimer des produits
- ❌ Accéder au dashboard admin
- ❌ Gérer les stocks

### 2. Vendeur (vendor)
**Description:** Vendeur qui gère son catalogue de produits sur la plateforme.

**Permissions:**
- ✅ Toutes les permissions du client
- ✅ Créer des produits (POST /api/products)
- ✅ Modifier ses produits (PUT /api/products/{id})
- ✅ Supprimer ses produits (DELETE /api/products/{id})
- ✅ Gérer les stocks de ses produits (PUT /api/inventory/{id})
- ✅ Consulter les commandes de ses produits
- ❌ Modifier les produits d'autres vendeurs
- ❌ Accéder au dashboard admin complet

### 3. Administrateur (admin)
**Description:** Administrateur système avec accès complet à la plateforme.

**Permissions:**
- ✅ Toutes les permissions des clients et vendeurs
- ✅ Accéder au dashboard admin (GET /api/admin/*)
- ✅ Gérer tous les utilisateurs (POST/PUT/DELETE /api/users)
- ✅ Gérer tous les produits
- ✅ Gérer tous les stocks
- ✅ Consulter toutes les commandes
- ✅ Gérer tous les paiements
- ✅ Accéder aux métriques système (GET /metrics)
- ✅ Consulter les logs et monitoring

## Matrice de permissions

| Endpoint | Client | Vendor | Admin |
|----------|--------|--------|-------|
| GET /api/products | ✅ | ✅ | ✅ |
| POST /api/products | ❌ | ✅ (ses produits) | ✅ |
| PUT /api/products/{id} | ❌ | ✅ (ses produits) | ✅ |
| DELETE /api/products/{id} | ❌ | ✅ (ses produits) | ✅ |
| GET /api/users | ❌ | ❌ | ✅ |
| GET /api/users/me/profile | ✅ | ✅ | ✅ |
| POST /api/orders | ✅ | ✅ | ✅ |
| GET /api/orders | ✅ (ses commandes) | ✅ (ses produits) | ✅ |
| POST /api/payments | ✅ | ✅ | ✅ |
| GET /api/inventory/{id} | ✅ | ✅ | ✅ |
| PUT /api/inventory/{id} | ❌ | ✅ (ses produits) | ✅ |
| GET /api/notifications | ✅ (ses notifs) | ✅ (ses notifs) | ✅ |
| GET /api/admin/* | ❌ | ❌ | ✅ |
| GET /metrics | ❌ | ❌ | ✅ |

## Implémentation

### 1. Authentification via Keycloak
Tous les utilisateurs doivent s'authentifier via Keycloak pour obtenir un JWT token contenant leurs rôles.

### 2. Validation au niveau Gateway (NGINX)
Le gateway NGINX valide le JWT token et peut bloquer les requêtes non autorisées avant qu'elles n'atteignent les microservices.

### 3. Validation au niveau Microservice
Chaque microservice vérifie également le JWT token et les rôles pour appliquer le principe de **défense en profondeur**.

### 4. Vérification de propriété (Ownership)
Pour les ressources appartenant à un utilisateur spécifique (commandes, produits d'un vendeur), le microservice vérifie que l'utilisateur authentifié est bien le propriétaire de la ressource.

## Principe Zero Trust appliqué

1. **Ne jamais faire confiance, toujours vérifier**
   - Chaque requête est validée, même si elle vient d'un réseau interne
   - Double validation: Gateway + Microservice

2. **Moindre privilège**
   - Chaque rôle a uniquement les permissions nécessaires
   - Pas d'accès par défaut

3. **Segmentation**
   - Isolation réseau entre les couches (frontend, backend, database)
   - Chaque microservice a sa propre base de données

4. **Audit complet**
   - Toutes les actions sont loguées avec l'identité de l'utilisateur
   - Traçabilité complète pour la conformité

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

Les rôles sont configurés dans le realm "ecommerce" avec:
- Realm roles: admin, vendor, client
- Client scopes: microservices (contient les claims de rôles)
- Protocol mappers: Inclut les rôles dans le JWT token

## Recommandations de sécurité

1. ✅ Utiliser HTTPS/TLS en production
2. ✅ Activer MFA (Multi-Factor Authentication) pour les admins
3. ✅ Rotation régulière des secrets Keycloak
4. ✅ Audit logs centralisés
5. ✅ Rate limiting par rôle (admins ont des limites plus élevées)
6. ✅ Session timeout approprié (15min pour clients, 30min pour admins)
7. ✅ Validation stricte des JWT (signature, expiration, issuer)
