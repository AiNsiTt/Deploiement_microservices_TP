#!/bin/bash

# Script de génération de certificats TLS auto-signés
# Architecture Microservices Zero Trust
# Auteur: Quentin Chaillou

set -e

echo "=== Génération des certificats TLS pour NGINX Gateway ==="

# Créer le répertoire si nécessaire
mkdir -p /tmp/certs

# Générer la clé privée
echo "1. Génération de la clé privée..."
openssl genrsa -out server.key 2048

# Générer le certificat auto-signé (valide 365 jours)
echo "2. Génération du certificat auto-signé..."
openssl req -new -x509 -key server.key -out server.crt -days 365 \
  -subj "/C=FR/ST=IDF/L=Paris/O=SPV M1 CS/OU=Architecture Microservices/CN=localhost"

# Générer le certificat CA (Certificate Authority)
echo "3. Génération du certificat CA..."
openssl genrsa -out ca.key 2048
openssl req -new -x509 -key ca.key -out ca.crt -days 365 \
  -subj "/C=FR/ST=IDF/L=Paris/O=SPV M1 CS/OU=CA/CN=ecommerce-ca"

# Générer les certificats clients (pour mTLS)
echo "4. Génération des certificats clients..."
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr \
  -subj "/C=FR/ST=IDF/L=Paris/O=SPV M1 CS/OU=Client/CN=client"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out client.crt -days 365

# Générer DH parameters pour Perfect Forward Secrecy
echo "5. Génération des paramètres Diffie-Hellman..."
openssl dhparam -out dhparam.pem 2048

echo ""
echo "=== Certificats générés avec succès ==="
echo "Fichiers créés:"
echo "  - server.key : Clé privée du serveur"
echo "  - server.crt : Certificat du serveur"
echo "  - ca.key     : Clé privée CA"
echo "  - ca.crt     : Certificat CA"
echo "  - client.key : Clé privée client"
echo "  - client.crt : Certificat client"
echo "  - dhparam.pem: Paramètres DH"
echo ""
echo "⚠️  ATTENTION: Ces certificats sont auto-signés et destinés au développement uniquement!"
echo "⚠️  En production, utilisez des certificats signés par une CA reconnue (Let's Encrypt, etc.)"
echo ""

# Afficher les informations du certificat
echo "=== Informations du certificat serveur ==="
openssl x509 -in server.crt -text -noout | grep -A 2 "Subject:"
openssl x509 -in server.crt -text -noout | grep -A 2 "Validity"
