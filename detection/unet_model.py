"""Module d'inférence U-Net pour la détection de maladies foliaires.

Mode démonstration par défaut. Pour connecter un vrai modèle Keras/TensorFlow,
remplacez la fonction load_model avec le chemin vers votre fichier .h5.
"""
import numpy as np
from PIL import Image, ImageFilter
import io
import base64


def load_model(path=None):
    """Charge le modèle U-Net. path=None active le mode démonstration."""
    if path is None:
        return {'mode': 'demo'}
    try:
        from tensorflow.keras.models import load_model as keras_load
        return {'mode': 'real', 'model': keras_load(path)}
    except Exception as exc:
        print(f"Avertissement : échec du chargement du modèle ({exc}). Mode démo activé.")
        return {'mode': 'demo'}


# Modèle chargé une seule fois au démarrage
MODEL = load_model(path=None)


def _image_to_data_uri(img_array):
    """Convertit un tableau numpy (H,W,3) en data URI base64."""
    img = Image.fromarray(img_array.astype(np.uint8))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    data = base64.b64encode(buffer.getvalue()).decode('ascii')
    return f'data:image/png;base64,{data}'


def analyze_image(pil_image, alpha=0.45):
    """Analyse une image PIL et retourne la segmentation complète.

    Args:
        pil_image: Image PIL à analyser
        alpha: Transparence du masque de superposition (0.1 à 0.9)

    Returns:
        dict: résultats d'analyse avec classe prédite, pourcentages,
              images encodées en base64, et niveaux de confiance
    """
    img = pil_image.convert('RGB').resize((256, 256))
    arr = np.array(img) / 255.0

    if MODEL.get('mode') == 'demo':
        # Mode démo : simulation basée sur la luminance pour générer un masque plausible
        gray = np.mean(arr, axis=2)
        mask = (gray < 0.4).astype(np.float32)
        mask_pil = Image.fromarray((mask * 255).astype(np.uint8))
        mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(radius=2))
        mask = np.array(mask_pil) / 255.0
    else:
        pred = MODEL['model'].predict(arr[np.newaxis, ...])[0]
        mask = pred[:, :, 0] if pred.ndim == 3 else pred

    # Calcul des statistiques
    total_pixels = mask.size
    disease_pixels = int(np.sum(mask > 0.5))
    healthy_pixels = total_pixels - disease_pixels
    disease_pct = round(disease_pixels / total_pixels * 100, 1)
    healthy_pct = round(healthy_pixels / total_pixels * 100, 1)

    # Construction des images de sortie
    mask_rgb = np.zeros((256, 256, 3), dtype=np.uint8)
    mask_rgb[mask > 0.5] = [183, 28, 28]    # rouge vif = zones infectées
    mask_rgb[mask <= 0.5] = [46, 125, 50]   # vert foncé = zones saines
    original_rgb = (arr * 255).astype(np.uint8)
    overlay = (arr * 255 * (1 - alpha) + mask_rgb * alpha).astype(np.uint8)

    # Classe prédite et confiance
    if disease_pct > 10:
        predicted_class = 'Maladie foliaire détectée'
        predicted_state = 'diseased'
    else:
        predicted_class = 'Plante saine'
        predicted_state = 'healthy'

    confidence = {
        'Plante saine': round(max(0.05, 1 - disease_pct / 100) * 100),
        'Maladie foliaire': round(min(0.95, disease_pct / 100) * 100),
        'Arrière-plan': 8,
    }

    return {
        'predicted_class': predicted_class,
        'predicted_state': predicted_state,
        'disease_pct': disease_pct,
        'healthy_pct': healthy_pct,
        'original_image': _image_to_data_uri(original_rgb),
        'mask_image': _image_to_data_uri(mask_rgb),
        'overlay_image': _image_to_data_uri(overlay),
        'confidence': confidence,
    }
