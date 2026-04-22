#!/usr/bin/env bash
# Script de build exécuté par Render à chaque déploiement
set -o errexit

echo "=== 1. Mise à jour pip ==="
pip install --upgrade pip

echo "=== 2. Installation des dépendances ==="
pip install -r requirements.txt

echo "=== 3. Collecte des fichiers statiques ==="
python manage.py collectstatic --no-input --clear

echo "=== Vérification des fichiers statiques collectés ==="
ls staticfiles/css/ || echo "AVERTISSEMENT: dossier css introuvable"
ls staticfiles/js/  || echo "AVERTISSEMENT: dossier js introuvable"

echo "=== 4. Migrations de la base de données ==="
python manage.py migrate

echo "=== Build terminé avec succès ==="