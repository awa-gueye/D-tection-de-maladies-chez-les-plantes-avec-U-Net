#!/usr/bin/env bash
# Script de build exécuté par Render à chaque déploiement
set -o errexit

echo "=== 1. Variables d'environnement ==="
export DEBUG=False
export PYTHONUNBUFFERED=1

echo "=== 2. Mise à jour pip ==="
pip install --upgrade pip

echo "=== 3. Installation des dépendances ==="
pip install -r requirements.txt

echo "=== 4. Création du répertoire staticfiles ==="
mkdir -p staticfiles

echo "=== 5. Collecte des fichiers statiques ==="
python manage.py collectstatic --no-input --verbosity 3 2>&1

echo "=== 6. Vérification des fichiers statiques ==="
if [ -d "staticfiles" ]; then
    echo "✓ Dossier staticfiles existe"
    find staticfiles -type f | head -20
else
    echo "✗ ERREUR: dossier staticfiles n'existe pas!"
    exit 1
fi

echo "=== 7. Migrations de la base de données ==="
python manage.py migrate --verbosity 2

echo "=== ✓ Build completed successfully ==="

echo "=== Build terminé avec succès ==="
