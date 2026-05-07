# 🚀 Migration PyTorch → ONNX (Réduction RAM: -50%)

## Problème
- PyTorch + modèle U-Net = **500+ MB** de RAM
- Plan Render Free = **512 MB** (overflow!)
- Rendu: crashes constants

## Solution
- ONNX Runtime = **250-300 MB** de RAM
- Réduction de **50%** de la consommation mémoire
- Même performance, mais plus rapide!

---

## 📋 Étapes

### **Étape 1 : Télécharger le modèle PyTorch**

Le script `convert_to_onnx.py` va le télécharger automatiquement depuis Google Drive:

```bash
# Optionnel: Si vous l'avez déjà, continuez à l'étape 2
ls detection/models/unet_best.pth
```

### **Étape 2 : Convertir PyTorch → ONNX (LOCAL)**

**Sur votre machine (ne pas faire sur Render):**

```bash
# Assurez-vous que PyTorch est installé
pip install torch torchvision segmentation-models-pytorch

# Exécutez le script de conversion
python convert_to_onnx.py
```

✅ Cela va créer: `detection/models/unet_best.onnx` (~150-200 MB)

### **Étape 3 : Remplacer le fichier unet_model.py**

```bash
# Backup l'ancien fichier
mv detection/unet_model.py detection/unet_model_pytorch.py

# Utiliser la version ONNX
mv detection/unet_model_onnx.py detection/unet_model.py
```

### **Étape 4 : Mettre à jour requirements.txt**

```bash
# Sur Render, utiliser les dépendances ONNX (sans PyTorch)
cp requirements-onnx.txt requirements.txt
```

### **Étape 5 : Push sur Render**

```bash
git add -A
git commit -m "Migrate to ONNX runtime (-50% RAM consumption)"
git push
```

---

## ✅ Vérification

Après le déploiement sur Render:

1. Allez sur: https://phytoscan-0fva.onrender.com
2. Testez la détection d'image
3. Vérifiez les logs pour "✓ ONNX Runtime disponible"

---

## 📊 Comparaison

| Aspect | PyTorch | ONNX |
|--------|---------|------|
| **RAM au démarrage** | ~300 MB | ~50 MB |
| **RAM + modèle** | 500+ MB | 250-300 MB |
| **Temps inférence** | 100-200ms | 50-100ms |
| **Taille fichier** | ~500 MB | ~150-200 MB |

---

## ⚠️ Troubleshooting

**"Modèle ONNX non trouvé"**
```bash
# Vérifiez que la conversion a fonctionné
ls -la detection/models/
# Doit y avoir: unet_best.onnx
```

**"ONNX Runtime non disponible"**
```bash
pip install onnxruntime
```

**Mode démo activé (image grise avec masque aléatoire)**
- Vérifiez que `unet_best.onnx` existe
- Vérifiez les logs Render pour les erreurs

---

## 🔄 Rollback (revenir à PyTorch)

```bash
mv detection/unet_model.py detection/unet_model_onnx.py
mv detection/unet_model_pytorch.py detection/unet_model.py
cp requirements.txt requirements-backup.txt
# ... restaurer l'ancien requirements.txt
git push
```
