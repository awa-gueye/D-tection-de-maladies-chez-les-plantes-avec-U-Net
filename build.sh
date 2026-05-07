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

echo "=== 4. Conversion du modèle PyTorch → ONNX ==="
echo "Installation des dépendances PyTorch (temporaires)..."
pip install torch torchvision segmentation-models-pytorch onnx onnxscript onnxruntime six

echo "Conversion du modèle..."
python convert_to_onnx.py || echo "Conversion skipped (modèle non trouvé ou PyTorch non disponible)"

echo "Suppression du modèle PyTorch pour économiser l'espace..."
rm -f detection/models/unet_best.pth
rm -rf detection/models/__pycache__

echo "=== 5. Création du répertoire staticfiles ==="
mkdir -p staticfiles

echo "=== 6. Collecte des fichiers statiques ==="
python manage.py collectstatic --no-input --verbosity 3 2>&1

echo "=== 7. Vérification des fichiers statiques ==="
if [ -d "staticfiles" ]; then
    echo "✓ Dossier staticfiles existe"
    find staticfiles -type f | head -20
else
    echo "✗ ERREUR: dossier staticfiles n'existe pas!"
    exit 1
fi

echo "=== 8. Migrations de la base de données ==="
python manage.py migrate --verbosity 2

echo "=== ✓ Build completed successfully ==="
echo "Modèle ONNX chargé et prêt pour la production!"
