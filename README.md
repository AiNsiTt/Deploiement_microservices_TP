# Architecture Microservices Zero Trust - E-Commerce Platform

**Auteur :** Quentin Chaillou  
**Date :** Novembre 2025  
**Module :** Architecture Microservices & Sécurité  
**Formation :** SPV Master 1 Cybersécurité 2025

---

## 1. Présentation du Projet

Ce projet consiste en la conception et l'implémentation d'une plateforme e-commerce moderne et sécurisée, basée sur une architecture microservices. L'objectif principal est de démontrer la maîtrise des concepts d'architecture distribuée tout en appliquant rigoureusement les principes de sécurité Zero Trust et de la triade CIA (Confidentialité, Intégrité, Disponibilité).

La plateforme simule les fonctionnalités essentielles d'un site e-commerce, avec une authentification et une gestion des autorisations centralisées via Keycloak. L'ensemble de l'infrastructure est containerisé avec Docker et orchestré via Docker Compose pour un déploiement local simple et reproductible.

### Objectifs

Le projet vise à concevoir une architecture microservices pure, où chaque service est indépendant, déployable et scalable. Il s'agit également d'implémenter une sécurité Zero Trust, en s'assurant que chaque requête est authentifiée et autorisée, quel que soit son origine. L'architecture garantit la triade CIA à travers des mécanismes de chiffrement, de contrôle d'accès, de validation de données et de haute disponibilité. Enfin, une observabilité complète est mise en place avec un logging et un monitoring centralisés.

### Périmètre Fonctionnel

La plateforme est composée des microservices suivants pour couvrir le périmètre fonctionnel attendu :

| Microservice | Port | Description |
|---|---|---|
| **User Service** | 8001 | Gestion des utilisateurs (clients, vendeurs, administrateurs) |
| **Product Service** | 8002 | Gestion du catalogue de produits avec recherche avancée |
| **Order Service** | 8003 | Workflow complet de gestion des commandes |
| **Payment Service** | 8004 | Simulation de traitement des paiements sécurisés |
| **Inventory Service** | 8005 | Gestion des stocks et de l'inventaire |
| **Notification Service** | 8006 | Envoi de notifications temps réel |
| **Admin Dashboard** | 8007 | Service d'agrégation pour le tableau de bord administrateur |

---

## 2. Architecture Générale

L'architecture est conçue en plusieurs couches logiques pour assurer la séparation des préoccupations, la sécurité et la scalabilité. Le modèle C4 est utilisé pour visualiser l'architecture à différents niveaux de détail.

### Diagramme de Contexte (Niveau 1)

Ce diagramme montre la vue d'ensemble du système et ses interactions avec les utilisateurs et les systèmes externes.

![Diagramme de Contexte C4](architecture/c4-context.png)

### Diagramme de Conteneurs (Niveau 2)

Ce diagramme détaille les conteneurs (microservices, bases de données, etc.) qui composent la plateforme e-commerce.

![Diagramme de Conteneurs C4](architecture/c4-container.png)

### Couches de l'architecture

L'architecture est organisée en plusieurs couches distinctes. La **Gateway Layer** utilise un API Gateway NGINX qui sert de point d'entrée unique. Il gère le routage, la terminaison TLS, le load balancing, le rate limiting et une première couche de validation de sécurité.

La couche **Security & Identity** repose sur Keycloak, utilisé comme Identity Provider (IdP) central. Il gère l'authentification via OAuth2/OIDC et la définition des rôles selon le modèle RBAC.

La **Microservices Layer** constitue le cœur de l'application, où chaque service métier est implémenté en Python avec le framework FastAPI, choisi pour sa performance et sa simplicité.

La **Data Layer** applique le pattern Database-per-Service : chaque microservice possède sa propre base de données PostgreSQL pour garantir l'isolation. Redis est utilisé pour le caching.

Enfin, l'**Observability Layer** comprend une stack de monitoring complète avec Prometheus pour la collecte de métriques, Grafana pour la visualisation et les dashboards, et Loki pour l'agrégation des logs.

---

## 3. Explication des Méthodes & Outils pour le Zero Trust et la Triade CIA

### Sécurité Zero Trust

Le principe fondamental du Zero Trust est de ne jamais faire confiance et de toujours vérifier. Chaque requête, même interne au réseau, doit être authentifiée et autorisée.

![Flux de Sécurité Zero Trust](architecture/zero-trust-flow.png)

Ce principe est appliqué dans l'architecture de plusieurs manières. L'**authentification forte** est obligatoire : toute interaction commence par une authentification via Keycloak. Les microservices ne communiquent jamais sans un JSON Web Token (JWT) valide.

La **défense en profondeur** est mise en œuvre par une double validation du token : d'abord au niveau de l'API Gateway (NGINX), puis une seconde fois au sein de chaque microservice. Cela garantit que même si le gateway est compromis, la sécurité interne reste intacte.

Le **contrôle d'accès granulaire (RBAC)** est géré par Keycloak qui définit des rôles (client, vendeur, admin) inclus dans le JWT. Chaque microservice utilise ces rôles pour autoriser ou refuser l'accès à ses endpoints de manière granulaire.

La **segmentation réseau** est assurée par l'isolation des conteneurs dans des réseaux Docker distincts (frontend, backend, database). Le réseau database est configuré comme internal, ce qui signifie qu'il n'est pas accessible depuis l'extérieur, ni même depuis le gateway, mais uniquement par les microservices du backend.

Le **chiffrement end-to-end** protège la communication en transit via TLS/HTTPS depuis le client jusqu'à l'API Gateway.

### Triade CIA (Confidentialité, Intégrité, Disponibilité)

La sécurité de la plateforme est construite autour des trois piliers de la triade CIA.

![Diagramme de la Triade CIA](architecture/cia-triad.png)

#### Confidentialité

La confidentialité est assurée par plusieurs mécanismes. Le chiffrement en transit (TLS/HTTPS) est configuré au niveau du Gateway NGINX. Le contrôle d'accès RBAC via Keycloak garantit que seuls les utilisateurs autorisés accèdent aux données. L'isolation des bases de données dans un réseau interne protège les données sensibles. La gestion des secrets est effectuée via des variables d'environnement Docker, évitant les secrets hardcodés dans le code source.

#### Intégrité

L'intégrité des données est garantie par la signature et la validation des JWT, qui empêchent toute altération des tokens. La validation des données à l'entrée de chaque API est assurée grâce à Pydantic dans FastAPI. Les contraintes transactionnelles et référentielles dans les bases de données PostgreSQL maintiennent la cohérence des données. Des logs d'audit complets tracent toutes les actions sensibles pour assurer la traçabilité.

#### Disponibilité

La disponibilité est assurée par plusieurs mécanismes de résilience. Le load balancing est implicite via les configurations upstream de NGINX. Les health checks dans Docker Compose permettent de redémarrer automatiquement les services défaillants. Les politiques de redémarrage (restart: unless-stopped) assurent la résilience des services. Le rate limiting sur NGINX protège contre les attaques par déni de service (DDoS). Le monitoring et les alertes avec Prometheus et Grafana permettent de détecter et réagir rapidement aux pannes.

### Outils Utilisés

| Outil | Rôle dans le projet |
|---|---|
| **Docker / Docker Compose** | Containerisation de l'ensemble des services et orchestration locale |
| **NGINX** | API Gateway, reverse proxy, load balancing, terminaison TLS, sécurité |
| **Keycloak** | Fournisseur d'identité (IdP) pour l'authentification et l'autorisation (OAuth2/OIDC, RBAC) |
| **Python / FastAPI** | Framework de développement des microservices, choisi pour sa performance et sa robustesse |
| **PostgreSQL** | Système de gestion de base de données relationnelle pour chaque microservice |
| **Redis** | Cache distribué pour améliorer les performances |
| **Prometheus** | Collecte des métriques de performance et de santé des services |
| **Grafana** | Visualisation des métriques et création de dashboards de monitoring |
| **Loki** | Agrégation et consultation des logs de tous les services |

---

## 4. Autres Considérations et Remarques

### Choix Technologiques

FastAPI (Python) a été choisi pour sa syntaxe moderne basée sur l'injection de dépendances, sa validation de données native avec Pydantic, sa génération automatique de documentation OpenAPI, et ses excellentes performances, ce qui en fait un candidat idéal pour les microservices.

NGINX a été préféré à d'autres gateways comme Kong ou Traefik pour sa légèreté, sa flexibilité et sa large adoption dans l'industrie. Sa configuration, bien que manuelle, offre un contrôle très fin sur le routage et la sécurité.

PostgreSQL, une base de données relationnelle robuste et éprouvée, est parfaitement adaptée aux besoins transactionnels d'une plateforme e-commerce.

### Défis Rencontrés et Solutions

La configuration de Keycloak peut être complexe. La solution adoptée a été de créer un fichier de configuration de realm (realm-config.json) qui peut être importé pour automatiser la création des rôles, clients et utilisateurs, rendant le setup reproductible.

Assurer que les appels entre microservices sont sécurisés constitue un défi majeur. La solution adoptée est de propager le JWT token initial de l'utilisateur lors des appels internes, permettant à chaque service de valider l'identité et les permissions de l'appelant originel.

### Améliorations Possibles

Pour une gestion plus avancée de la sécurité et de l'observabilité inter-services, l'intégration d'un service mesh comme Istio ou Linkerd serait une étape logique. Cela permettrait d'implémenter le mTLS (mutual TLS) de manière transparente.

La mise en place d'une pipeline d'intégration et de déploiement continus (avec GitHub Actions, GitLab CI) permettrait d'automatiser les tests, la construction des images Docker et le déploiement.

Le remplacement des bases de données en mémoire utilisées pour la simulation dans certains services par de vraies instances PostgreSQL assurerait une persistance complète des données.

Le développement de scénarios de tests plus complets, incluant des tests d'intégration, des tests de charge et des tests de pénétration, permettrait de valider la robustesse et la sécurité de l'architecture.

### Justification de l'Architecture pour un Contexte Professionnel

Cette architecture présente plusieurs avantages significatifs. La scalabilité est assurée car chaque service peut être scalé indépendamment selon la charge. La résilience est garantie puisque la défaillance d'un service n'affecte pas les autres. La sécurité est renforcée par le modèle Zero Trust qui garantit qu'aucune confiance implicite n'est accordée. La maintenabilité est facilitée par un code modulaire où chaque équipe peut travailler sur un service indépendamment. Enfin, l'observabilité complète permet de détecter et résoudre les problèmes rapidement.

---

## Guide de Démarrage

Pour des instructions détaillées sur l'installation, la configuration et le test de la plateforme, veuillez consulter le guide de démarrage rapide : [QUICKSTART.md](QUICKSTART.md)

### Commande de base

```bash
# Naviguer dans le dossier de l'infrastructure
cd infrastructure

# Démarrer tous les services en arrière-plan
docker-compose up -d
```

### Accès aux interfaces

| Service | URL | Identifiants |
|---------|-----|--------------|
| API Gateway | http://localhost | - |
| Keycloak | http://localhost:8080 | admin / admin123 |
| Grafana | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | - |
