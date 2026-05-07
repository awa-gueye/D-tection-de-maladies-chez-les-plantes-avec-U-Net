"""
unet_model.py — Inférence U-Net PyTorch pour PhytoScan AI (Django).

Remplace le mode démonstration par le vrai modèle entraîné sur PlantVillage.
Interface identique à l'original : analyze_image() retourne le même dict.

Placement du checkpoint :
    detection/models/unet_best.pth
    OU défini via variable d'environnement MODEL_PATH
"""
import os
import io
import base64

import numpy as np
from PIL import Image, ImageFilter

# ─── Imports PyTorch (optionnels — fallback démo si absent) ────────────────
try:
    import torch
    import torch.nn as nn
    import cv2
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch non disponible — mode démo activé.")

try:
    import segmentation_models_pytorch as smp
    SMP_AVAILABLE = True
except ImportError:
    SMP_AVAILABLE = False
    print("Warning: segmentation_models_pytorch non disponible.")


# ═══════════════════════════════════════════════════════════════════════════ #
#  Configuration                                                               #
# ═══════════════════════════════════════════════════════════════════════════ #

# Chemin vers le checkpoint — modifiable via variable d'environnement
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "models", "unet_best.pth")
MODEL_PATH = os.environ.get("MODEL_PATH", DEFAULT_MODEL_PATH)

# Paramètres identiques à l'entraînement
IMAGE_SIZE  = 256
MEAN        = (0.485, 0.456, 0.406)
STD         = (0.229, 0.224, 0.225)
THRESHOLD   = 0.5
DEVICE      = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"


# ═══════════════════════════════════════════════════════════════════════════ #
#  Chargement du modèle                                                        #
# ═══════════════════════════════════════════════════════════════════════════ #

def load_model(path=None):
    """
    Charge le modèle U-Net PyTorch.
    Retourne un dict {'mode': 'real', 'model': ...} ou {'mode': 'demo'}.
    """
    if path is None:
        path = MODEL_PATH

    # Vérifie les dépendances
    if not TORCH_AVAILABLE or not SMP_AVAILABLE:
        print("Mode démo : PyTorch ou smp non disponible.")
        return {"mode": "demo"}

    # Vérifie que le fichier existe
    if not os.path.exists(path):
        print(f"Checkpoint introuvable : {path}")
        print("→ Mode démo activé. Placez unet_best.pth dans detection/models/")
        return {"mode": "demo"}

    try:
        checkpoint = torch.load(path, map_location=DEVICE)
        cfg = checkpoint.get("model_config", {})

        model = smp.Unet(
            encoder_name    = cfg.get("encoder_name", "resnet50"),
            encoder_weights = None,
            in_channels     = cfg.get("in_channels", 3),
            classes         = cfg.get("num_classes", 1),
            activation      = cfg.get("activation", None),
        )
        model.load_state_dict(checkpoint["model_state"])
        model.to(DEVICE).eval()

        epoch   = checkpoint.get("epoch", "?")
        val_iou = checkpoint.get("val_iou", 0)
        print(f"Modèle U-Net chargé ✓ | epoch={epoch} | val_IoU={val_iou:.4f} | device={DEVICE}")

        return {"mode": "real", "model": model}

    except Exception as e:
        print(f"Erreur chargement modèle ({e}) → mode démo activé.")
        return {"mode": "demo"}


# ─── Modèle chargé une seule fois au démarrage de Django ───────────────────
MODEL = load_model()


# ═══════════════════════════════════════════════════════════════════════════ #
#  Prétraitement / Post-traitement                                             #
# ═══════════════════════════════════════════════════════════════════════════ #

def _preprocess(pil_image: Image.Image) -> "torch.Tensor":
    """PIL RGB → Tensor [1, 3, H, W] normalisé."""
    img_rgb = np.array(pil_image.convert("RGB"))
    transform = A.Compose([
        A.Resize(IMAGE_SIZE, IMAGE_SIZE),
        A.Normalize(mean=MEAN, std=STD),
        ToTensorV2(),
    ])
    tensor = transform(image=img_rgb)["image"]
    return tensor.unsqueeze(0).to(DEVICE)


def _predict_mask(model: "nn.Module", tensor: "torch.Tensor") -> np.ndarray:
    """Retourne un masque binaire numpy [H, W] (0.0 ou 1.0)."""
    with torch.no_grad():
        logits = model(tensor)
        prob   = torch.sigmoid(logits[0, 0]).cpu().numpy()
    return (prob > THRESHOLD).astype(np.float32)


def _demo_mask(arr: np.ndarray) -> np.ndarray:
    """Masque de démonstration basé sur la luminance."""
    gray = np.mean(arr, axis=2)
    mask = (gray < 0.4).astype(np.float32)
    mask_pil = Image.fromarray((mask * 255).astype(np.uint8))
    mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(radius=2))
    return np.array(mask_pil) / 255.0


def _image_to_data_uri(img_array: np.ndarray) -> str:
    """Convertit un tableau numpy (H,W,3) en data URI base64 PNG."""
    img    = Image.fromarray(img_array.astype(np.uint8))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    data = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{data}"


# ═══════════════════════════════════════════════════════════════════════════ #
#  Fonction principale — interface identique à l'original                     #
# ═══════════════════════════════════════════════════════════════════════════ #

def analyze_image(pil_image: Image.Image, alpha: float = 0.45) -> dict:
    """
    Analyse une image PIL et retourne la segmentation complète.

    Args:
        pil_image : Image PIL à analyser
        alpha     : Transparence du masque de superposition (0.1 à 0.9)

    Returns:
        dict avec : predicted_class, predicted_state, disease_pct,
                    healthy_pct, original_image, mask_image,
                    overlay_image, confidence
    """
    img     = pil_image.convert("RGB").resize((IMAGE_SIZE, IMAGE_SIZE))
    arr     = np.array(img) / 255.0   # [H, W, 3] float64 [0, 1]

    # ── Génération du masque ─────────────────────────────────────────────
    if MODEL.get("mode") == "real" and TORCH_AVAILABLE:
        tensor = _preprocess(img)
        mask   = _predict_mask(MODEL["model"], tensor)
    else:
        mask = _demo_mask(arr)

    # ── Statistiques ─────────────────────────────────────────────────────
    total_pixels   = mask.size
    disease_pixels = int(np.sum(mask > 0.5))
    healthy_pixels = total_pixels - disease_pixels
    disease_pct    = round(disease_pixels / total_pixels * 100, 1)
    healthy_pct    = round(healthy_pixels / total_pixels * 100, 1)

    # ── Images de sortie ─────────────────────────────────────────────────
    mask_rgb = np.zeros((IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8)
    mask_rgb[mask > 0.5]  = [183, 28, 28]   # rouge  = zones malades
    mask_rgb[mask <= 0.5] = [46, 125, 50]   # vert   = zones saines

    original_rgb = (arr * 255).astype(np.uint8)
    overlay      = (arr * 255 * (1 - alpha) + mask_rgb * alpha).astype(np.uint8)

    # ── Classification ────────────────────────────────────────────────────
    if disease_pct > 30:
        predicted_class = "Maladie foliaire sévère"
        predicted_state = "diseased"
    elif disease_pct > 10:
        predicted_class = "Maladie foliaire détectée"
        predicted_state = "diseased"
    else:
        predicted_class = "Plante saine"
        predicted_state = "healthy"

    confidence = {
        "Plante saine":      round(max(0.05, 1 - disease_pct / 100) * 100),
        "Maladie foliaire":  round(min(0.95, disease_pct / 100) * 100),
        "Arrière-plan":      8,
    }

    return {
        "predicted_class": predicted_class,
        "predicted_state": predicted_state,
        "disease_pct":     disease_pct,
        "healthy_pct":     healthy_pct,
        "original_image":  _image_to_data_uri(original_rgb),
        "mask_image":      _image_to_data_uri(mask_rgb),
        "overlay_image":   _image_to_data_uri(overlay),
        "confidence":      confidence,
        "model_mode":      MODEL.get("mode", "demo"),
    }
