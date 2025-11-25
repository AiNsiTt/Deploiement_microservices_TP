# Structure du Projet

## Architecture Microservices Zero Trust - E-Commerce Platform
**Auteur:** Quentin Chaillou

```
SPV_M1_CS_2025_Architecture_Microservice/
│
├── README.md                           # Documentation principale du projet
├── QUICKSTART.md                       # Guide de démarrage rapide
├── STRUCTURE.md                        # Ce fichier - Description de la structure
├── .env.example                        # Template des variables d'environnement
├── .gitignore                          # Fichiers à ignorer par Git
│
├── architecture/                       # Schémas et diagrammes d'architecture
│   ├── c4-context.mmd                 # Diagramme C4 niveau 1 (Contexte)
│   ├── c4-context.png                 # Version PNG du diagramme
│   ├── c4-container.mmd               # Diagramme C4 niveau 2 (Conteneurs)
│   ├── c4-container.png               # Version PNG du diagramme
│   ├── zero-trust-flow.mmd            # Flux de sécurité Zero Trust
│   ├── zero-trust-flow.png            # Version PNG du flux
│   ├── cia-triad.mmd                  # Diagramme de la triade CIA
│   └── cia-triad.png                  # Version PNG de la triade
│
├── microservices/                      # Code source des microservices
│   │
│   ├── user-service/                  # Service de gestion des utilisateurs
│   │   ├── app.py                     # Application FastAPI
│   │   ├── Dockerfile                 # Image Docker
│   │   └── requirements.txt           # Dépendances Python
│   │
│   ├── product-service/               # Service de gestion du catalogue
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── order-service/                 # Service de gestion des commandes
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── payment-service/               # Service de traitement des paiements
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── inventory-service/             # Service de gestion des stocks
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── notification-service/          # Service de notifications
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── admin-dashboard/               # Tableau de bord administrateur
│       ├── app.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── infrastructure/                     # Infrastructure as Code
│   │
│   ├── docker-compose.yml             # Orchestration de tous les services
│   │
│   ├── keycloak/                      # Configuration Keycloak
│   │   └── realm-config.json          # Configuration du realm ecommerce
│   │
│   └── monitoring/                    # Configuration du monitoring
│       ├── prometheus.yml             # Configuration Prometheus
│       └── grafana/                   # Dashboards et datasources Grafana
│           ├── dashboards/
│           └── datasources/
│
├── gateway/                            # API Gateway
│   └── nginx/                         # Configuration NGINX
│       ├── nginx.conf                 # Configuration principale
│       └── conf.d/                    # Configurations additionnelles
│
├── security/                           # Configuration sécurité
│   │
│   ├── certificates/                  # Certificats TLS
│   │   ├── generate-certs.sh          # Script de génération
│   │   └── README.md                  # Instructions
│   │
│   ├── policies/                      # Politiques de sécurité
│   │   └── (fichiers de politiques)
│   │
│   └── rbac/                          # Contrôle d'accès basé sur les rôles
│       └── policies.md                # Documentation RBAC détaillée
│
└── demo/                               # Démonstration et tests
    │
    ├── screenshots/                   # Captures d'écran (obligatoire)
    │   └── README.md                  # Guide pour les captures
    │
    ├── test-scenarios/                # Scénarios de test
    │   ├── scenario-1-authentication.md
    │   └── scenario-2-order-workflow.md
    │
    └── postman-collection.json        # Collection Postman (optionnel)
```

## Description des Composants

### Architecture (`architecture/`)
Contient tous les diagrammes d'architecture au format Mermaid (.mmd) et leurs versions PNG. Les diagrammes suivent le modèle C4 pour une visualisation à plusieurs niveaux de détail.

### Microservices (`microservices/`)
Chaque microservice est une application Python FastAPI autonome avec :
- **app.py** : Code de l'application avec endpoints REST
- **Dockerfile** : Configuration de containerisation
- **requirements.txt** : Dépendances Python

Tous les microservices suivent la même structure pour faciliter la maintenance.

### Infrastructure (`infrastructure/`)
- **docker-compose.yml** : Orchestre tous les services (microservices, bases de données, Keycloak, monitoring)
- **keycloak/** : Configuration du realm, rôles et utilisateurs
- **monitoring/** : Configuration de Prometheus et Grafana

### Gateway (`gateway/`)
Configuration de l'API Gateway NGINX qui sert de point d'entrée unique :
- Routage vers les microservices
- Terminaison TLS
- Rate limiting
- Validation JWT (en production)

### Security (`security/`)
- **certificates/** : Scripts et certificats TLS pour HTTPS
- **rbac/** : Documentation détaillée des politiques RBAC
- **policies/** : Autres politiques de sécurité

### Demo (`demo/`)
Matériel de démonstration :
- **screenshots/** : Captures d'écran obligatoires pour la validation
- **test-scenarios/** : Scénarios de test documentés
- **postman-collection.json** : Collection Postman pour tester l'API

## Technologies Utilisées

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Microservices | Python + FastAPI | 3.11 / 0.104.1 |
| API Gateway | NGINX | Alpine |
| Identity Provider | Keycloak | 23.0 |
| Databases | PostgreSQL | 15 |
| Cache | Redis | 7 |
| Monitoring | Prometheus + Grafana | Latest |
| Logs | Loki | Latest |
| Containerisation | Docker + Docker Compose | 20.10+ / 2.0+ |

## Ports Utilisés

| Service | Port | Description |
|---------|------|-------------|
| NGINX Gateway | 80, 443 | Point d'entrée HTTP/HTTPS |
| Keycloak | 8080 | Interface d'administration |
| User Service | 8001 | API utilisateurs |
| Product Service | 8002 | API produits |
| Order Service | 8003 | API commandes |
| Payment Service | 8004 | API paiements |
| Inventory Service | 8005 | API stocks |
| Notification Service | 8006 | API notifications |
| Admin Dashboard | 8007 | API admin |
| Prometheus | 9090 | Métriques |
| Grafana | 3000 | Dashboards |
| Loki | 3100 | Logs |

## Réseaux Docker

- **frontend** : Communication externe (clients → gateway)
- **backend** : Communication inter-services
- **database** : Isolation des bases de données (internal)

## Volumes Docker

- **postgres_data** : Données PostgreSQL
- **keycloak_data** : Données Keycloak
- **redis_data** : Données Redis
- **prometheus_data** : Métriques Prometheus
- **grafana_data** : Configuration Grafana

## Principes Architecturaux

1. **Microservices purs** : Chaque service est indépendant et déployable séparément
2. **Database per Service** : Chaque service a sa propre base de données
3. **API Gateway Pattern** : Point d'entrée unique via NGINX
4. **Zero Trust Security** : Authentification et autorisation à chaque niveau
5. **Observability** : Monitoring et logging centralisés
6. **Infrastructure as Code** : Tout est défini en code (Docker Compose)
