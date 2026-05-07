#!/usr/bin/env bash
# Script de build exécuté par Render à chaque déploiement
set -o errexit

echo "=== 1. Mise à jour pip ==="
pip install --upgrade pip

echo "=== 2. Installation des dépendances ==="
pip install -r requirements.txt

echo "=== 3. Collecte des fichiers statiques ==="
echo "Création du répertoire staticfiles..."
mkdir -p staticfiles

python manage.py collectstatic --no-input --verbosity 2

echo "=== Vérification des fichiers statiques collectés ==="
echo "Contenu de staticfiles:"
ls -la staticfiles/ || echo "ERREUR: dossier staticfiles introuvable"

echo "=== 4. Migrations de la base de données ==="
python manage.py migrate

echo "=== Build terminé avec succès ==="

echo "=== Build terminé avec succès ==="
