# Configuration Manuelle de Keycloak

## Guide de Configuration du Realm E-Commerce

Si l'import automatique du realm ne fonctionne pas correctement, suivez ces étapes pour configurer manuellement Keycloak.

---

## Étape 1 : Créer le Realm

1. Accéder à http://localhost:8080
2. Se connecter avec **admin** / **admin123**
3. Cliquer sur le menu déroulant en haut à gauche (actuellement sur "master")
4. Cliquer sur **"Create Realm"**
5. Renseigner :
   - **Realm name** : `ecommerce`
   - **Enabled** : ON
6. Cliquer sur **"Create"**

---

## Étape 2 : Créer les Rôles

1. Dans le menu de gauche, aller dans **Realm roles**
2. Cliquer sur **"Create role"**
3. Créer les 3 rôles suivants :

### Rôle 1 : client
- **Role name** : `client`
- **Description** : Client acheteur

### Rôle 2 : vendor
- **Role name** : `vendor`
- **Description** : Vendeur sur la plateforme

### Rôle 3 : admin
- **Role name** : `admin`
- **Description** : Administrateur de la plateforme

---

## Étape 3 : Créer le Client pour l'Authentification

1. Dans le menu de gauche, aller dans **Clients**
2. Cliquer sur **"Create client"**

### Configuration du client

**General Settings :**
- **Client type** : OpenID Connect
- **Client ID** : `ecommerce-frontend`
- Cliquer sur **"Next"**

**Capability config :**
- **Client authentication** : OFF (public client)
- **Authorization** : OFF
- **Standard flow** : ON
- **Direct access grants** : **ON** (IMPORTANT)
- **Implicit flow** : OFF
- Cliquer sur **"Next"**

**Login settings :**
- **Valid redirect URIs** : 
  - `http://localhost:3000/*`
  - `http://localhost/*`
- **Web origins** : 
  - `http://localhost:3000`
  - `http://localhost`
- Cliquer sur **"Save"**

---

## Étape 4 : Créer les Utilisateurs

### Utilisateur 1 : Client

1. Dans le menu de gauche, aller dans **Users**
2. Cliquer sur **"Create new user"**
3. Renseigner :
   - **Username** : `client1`
   - **Email** : `client@ecommerce.com`
   - **First name** : Jane
   - **Last name** : Client
   - **Email verified** : ON
4. Cliquer sur **"Create"**

**Définir le mot de passe :**
1. Aller dans l'onglet **Credentials**
2. Cliquer sur **"Set password"**
3. Renseigner :
   - **Password** : `client123`
   - **Password confirmation** : `client123`
   - **Temporary** : OFF
4. Cliquer sur **"Save"**

**Assigner le rôle :**
1. Aller dans l'onglet **Role mapping**
2. Cliquer sur **"Assign role"**
3. Sélectionner **"client"**
4. Cliquer sur **"Assign"**

### Utilisateur 2 : Vendor

Répéter les mêmes étapes avec :
- **Username** : `vendor1`
- **Email** : `vendor@ecommerce.com`
- **First name** : John
- **Last name** : Vendor
- **Password** : `vendor123`
- **Rôle** : vendor

### Utilisateur 3 : Admin

Répéter les mêmes étapes avec :
- **Username** : `admin`
- **Email** : `admin@ecommerce.com`
- **First name** : Admin
- **Last name** : System
- **Password** : `admin123`
- **Rôle** : admin

---

## Étape 5 : Tester l'Authentification

Une fois la configuration terminée, tester avec la commande suivante :

```bash
curl -X POST http://localhost:8080/realms/ecommerce/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=client1" \
  -d "password=client123" \
  -d "grant_type=password" \
  -d "client_id=ecommerce-frontend"
```

**Note importante :** Le chemin est `/realms/ecommerce` et non `/auth/realms/ecommerce` dans les versions récentes de Keycloak (23+).

### Résultat attendu

Vous devriez recevoir une réponse JSON contenant :
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI...",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
  "token_type": "Bearer"
}
```

---

## Résolution de Problèmes

### Erreur : "Unable to find matching target resource method"

**Cause :** Le client n'a pas l'option "Direct access grants" activée.

**Solution :**
1. Aller dans **Clients** → **ecommerce-frontend**
2. Aller dans l'onglet **Settings**
3. Vérifier que **"Direct access grants"** est **ON**
4. Cliquer sur **"Save"**

### Erreur : "Invalid user credentials"

**Cause :** Le mot de passe est incorrect ou l'utilisateur n'existe pas.

**Solution :**
1. Vérifier que l'utilisateur existe dans **Users**
2. Réinitialiser le mot de passe dans l'onglet **Credentials**
3. S'assurer que **"Temporary"** est **OFF**

### Erreur : "Client not found"

**Cause :** Le client_id est incorrect ou le client n'existe pas.

**Solution :**
1. Vérifier que le client "ecommerce-frontend" existe dans **Clients**
2. Vérifier l'orthographe du client_id dans la commande curl

---

## Vérification de la Configuration

Pour vérifier que tout est correctement configuré :

1. **Realm** : ecommerce existe et est activé
2. **Rôles** : client, vendor, admin existent
3. **Client** : ecommerce-frontend existe avec Direct access grants activé
4. **Utilisateurs** : client1, vendor1, admin existent avec leurs mots de passe
5. **Role mapping** : Chaque utilisateur a son rôle assigné

---

## Commandes de Test Complètes

### Test avec client1
```bash
curl -X POST http://localhost:8080/realms/ecommerce/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=client1" \
  -d "password=client123" \
  -d "grant_type=password" \
  -d "client_id=ecommerce-frontend"
```

### Test avec vendor1
```bash
curl -X POST http://localhost:8080/realms/ecommerce/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=vendor1" \
  -d "password=vendor123" \
  -d "grant_type=password" \
  -d "client_id=ecommerce-frontend"
```

### Test avec admin
```bash
curl -X POST http://localhost:8080/realms/ecommerce/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin" \
  -d "password=admin123" \
  -d "grant_type=password" \
  -d "client_id=ecommerce-frontend"
```
