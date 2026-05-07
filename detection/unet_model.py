"""
unet_model.py — Inférence U-Net PyTorch pour PhytoScan AI (Django).
Télécharge automatiquement le modèle depuis Google Drive au démarrage.
"""
import os
import io
import base64

import numpy as np
from PIL import Image, ImageFilter

# ─── Config ────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR      = os.path.join(BASE_DIR, "models")
MODEL_PATH     = os.path.join(MODEL_DIR, "unet_best.pth")
GDRIVE_FILE_ID = "1ZZOwjCiZpUmYLif2KyPc0y34il2Ecz30"
IMAGE_SIZE     = 256
MEAN           = (0.485, 0.456, 0.406)
STD            = (0.229, 0.224, 0.225)
THRESHOLD      = 0.5

# ─── Imports optionnels ─────────────────────────────────────────────────────
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch non disponible — mode démo activé.")

try:
    import segmentation_models_pytorch as smp
    SMP_AVAILABLE = True
except ImportError:
    SMP_AVAILABLE = False

try:
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
    ALB_AVAILABLE = True
except ImportError:
    ALB_AVAILABLE = False

DEVICE = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"


# ═══════════════════════════════════════════════════════════════════════════ #
#  Téléchargement automatique depuis Google Drive                             #
# ═══════════════════════════════════════════════════════════════════════════ #

def _download_model():
    """Télécharge le modèle depuis Google Drive si absent."""
    if os.path.exists(MODEL_PATH):
        size_mb = os.path.getsize(MODEL_PATH) / 1e6
        print(f"Modèle trouvé localement ({size_mb:.1f} MB) ✓")
        return True

    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"Téléchargement du modèle U-Net depuis Google Drive...")
    print(f"ID : {GDRIVE_FILE_ID}")

    try:
        import gdown
        url = f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}"
        gdown.download(url, MODEL_PATH, quiet=False)

        if os.path.exists(MODEL_PATH):
            size_mb = os.path.getsize(MODEL_PATH) / 1e6
            print(f"Modèle téléchargé ✓ ({size_mb:.1f} MB)")
            return True
        else:
            print("Échec : fichier non créé après téléchargement.")
            return False

    except Exception as e:
        print(f"Échec téléchargement gdown ({e})")
        # Fallback urllib
        try:
            import urllib.request
            url = f"https://drive.google.com/uc?export=download&id={GDRIVE_FILE_ID}"
            urllib.request.urlretrieve(url, MODEL_PATH)
            print(f"Modèle téléchargé via urllib ✓")
            return True
        except Exception as e2:
            print(f"Échec urllib ({e2}) → mode démo activé.")
            return False


# ═══════════════════════════════════════════════════════════════════════════ #
#  Chargement du modèle                                                        #
# ═══════════════════════════════════════════════════════════════════════════ #

def load_model(path=None):
    """Charge le modèle U-Net PyTorch."""
    if path is None:
        path = MODEL_PATH

    if not TORCH_AVAILABLE or not SMP_AVAILABLE:
        print("Mode démo : PyTorch ou smp non disponible.")
        return {"mode": "demo"}

    if not os.path.exists(path):
        print(f"Checkpoint introuvable : {path} → mode démo.")
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
        print(f"Erreur chargement modèle ({e}) → mode démo.")
        return {"mode": "demo"}


# ─── Téléchargement + chargement au démarrage Django ───────────────────────
_download_model()
MODEL = load_model()


# ═══════════════════════════════════════════════════════════════════════════ #
#  Prétraitement                                                               #
# ═══════════════════════════════════════════════════════════════════════════ #

def _preprocess(pil_image):
    """PIL RGB → Tensor [1, 3, H, W] normalisé."""
    img_rgb = np.array(pil_image.convert("RGB"))
    transform = A.Compose([
        A.Resize(IMAGE_SIZE, IMAGE_SIZE),
        A.Normalize(mean=MEAN, std=STD),
        ToTensorV2(),
    ])
    tensor = transform(image=img_rgb)["image"]
    return tensor.unsqueeze(0).to(DEVICE)


def _predict_mask(model, tensor):
    """Retourne un masque binaire numpy [H, W] (0.0 ou 1.0)."""
    with torch.no_grad():
        logits = model(tensor)
        prob   = torch.sigmoid(logits[0, 0]).cpu().numpy()
    return (prob > THRESHOLD).astype(np.float32)


def _demo_mask(arr):
    """Masque de démonstration basé sur la luminance."""
    gray = np.mean(arr, axis=2)
    mask = (gray < 0.4).astype(np.float32)
    mask_pil = Image.fromarray((mask * 255).astype(np.uint8))
    mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(radius=2))
    return np.array(mask_pil) / 255.0


def _image_to_data_uri(img_array):
    """Convertit un tableau numpy (H,W,3) en data URI base64 PNG."""
    img    = Image.fromarray(img_array.astype(np.uint8))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    data = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{data}"


# ═══════════════════════════════════════════════════════════════════════════ #
#  Fonction principale — interface identique à l'original                     #
# ═══════════════════════════════════════════════════════════════════════════ #

def analyze_image(pil_image, alpha=0.45):
    """
    Analyse une image PIL et retourne la segmentation complète.

    Args:
        pil_image : Image PIL à analyser
        alpha     : Transparence du masque de superposition (0.1 à 0.9)

    Returns:
        dict avec : predicted_class, predicted_state, disease_pct,
                    healthy_pct, original_image, mask_image,
                    overlay_image, confidence, model_mode
    """
    img = pil_image.convert("RGB").resize((IMAGE_SIZE, IMAGE_SIZE))
    arr = np.array(img) / 255.0

    # ── Génération du masque ─────────────────────────────────────────────
    if MODEL.get("mode") == "real" and TORCH_AVAILABLE and ALB_AVAILABLE:
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
    mask_rgb[mask > 0.5]  = [183, 28, 28]   # rouge = zones malades
    mask_rgb[mask <= 0.5] = [46, 125, 50]   # vert  = zones saines

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
        "Plante saine":     round(max(0.05, 1 - disease_pct / 100) * 100),
        "Maladie foliaire": round(min(0.95, disease_pct / 100) * 100),
        "Arrière-plan":     8,
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
