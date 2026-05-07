"""
Script pour convertir le modèle PyTorch U-Net en ONNX (beaucoup plus léger).
Usage: python convert_to_onnx.py
"""
import os
import sys
import torch
import numpy as np

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "detection", "models")
PYTORCH_MODEL = os.path.join(MODEL_DIR, "unet_best.pth")
ONNX_MODEL = os.path.join(MODEL_DIR, "unet_best.onnx")
IMAGE_SIZE = 256

print("=" * 70)
print("CONVERSION PyTorch → ONNX")
print("=" * 70)

# Vérifier PyTorch
try:
    import torch
    print("✓ PyTorch installé")
except ImportError:
    print("✗ Erreur: pip install torch")
    sys.exit(1)

try:
    import segmentation_models_pytorch as smp
    print("✓ segmentation_models_pytorch installé")
except ImportError as e:
    print(f"✗ Erreur import smp: {e}")
    print("  Essayez: pip install segmentation-models-pytorch")
    sys.exit(1)

# Vérifier le modèle PyTorch
if not os.path.exists(PYTORCH_MODEL):
    print(f"✗ Modèle PyTorch non trouvé: {PYTORCH_MODEL}")
    sys.exit(1)

print(f"✓ Modèle PyTorch trouvé: {PYTORCH_MODEL}")

# Charger le checkpoint PyTorch
print("\n1. Chargement du checkpoint PyTorch...")
device = "cuda" if torch.cuda.is_available() else "cpu"
checkpoint = torch.load(PYTORCH_MODEL, map_location=device)
print(f"   Clés du checkpoint: {list(checkpoint.keys())}")

# Créer le modèle
print("\n2. Création du modèle U-Net...")
cfg = checkpoint.get("model_config", {})
encoder_name = cfg.get("encoder_name", "resnet50")
in_channels = cfg.get("in_channels", 3)
num_classes = cfg.get("num_classes", 1)

print(f"   - Encoder: {encoder_name}")
print(f"   - Input channels: {in_channels}")
print(f"   - Output classes: {num_classes}")

model = smp.Unet(
    encoder_name=encoder_name,
    encoder_weights=None,
    in_channels=in_channels,
    classes=num_classes,
    activation=cfg.get("activation", None),
)

# Charger les poids
print("\n3. Chargement des poids du modèle...")
model.load_state_dict(checkpoint["model_state"])
model.to(device)
model.eval()
print("   ✓ Modèle chargé avec succès")

# Convertir en ONNX
print("\n4. Conversion en ONNX...")
print(f"   Cible: {ONNX_MODEL}")

# Créer dummy input
dummy_input = torch.randn(1, in_channels, IMAGE_SIZE, IMAGE_SIZE, device=device)

# Export ONNX
try:
    torch.onnx.export(
        model,
        dummy_input,
        ONNX_MODEL,
        input_names=["input"],
        output_names=["output"],
        opset_version=12,
        do_constant_folding=True,
        verbose=False,
    )
    print("   ✓ Conversion réussie!")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    sys.exit(1)

# Vérifier le fichier
if os.path.exists(ONNX_MODEL):
    pytorch_size = os.path.getsize(PYTORCH_MODEL) / 1e6
    onnx_size = os.path.getsize(ONNX_MODEL) / 1e6
    ratio = (1 - onnx_size / pytorch_size) * 100
    
    print(f"\n5. Résultats:")
    print(f"   PyTorch: {pytorch_size:.1f} MB")
    print(f"   ONNX:    {onnx_size:.1f} MB")
    print(f"   Réduction: {ratio:.1f}% 📉")
else:
    print("✗ Erreur: Le fichier ONNX n'a pas été créé")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ Conversion terminée avec succès!")
print("=" * 70)
print("\nProchaines étapes:")
print("1. pip install onnxruntime")
print("2. Remplacer les imports PyTorch par ONNX dans unet_model.py")
print("3. git add detection/models/unet_best.onnx")
print("4. git push")
