"""Vues de l'application detection — upload et analyse d'images."""
import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from PIL import Image

from .unet_model import analyze_image

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ACCEPTED_FORMATS = {'jpg', 'jpeg', 'png', 'webp'}


def detection_view(request):
    """Affiche la page de détection avec formulaire d'upload."""
    return render(request, 'detection/detection.html')


@require_http_methods(['POST'])
def api_analyze(request):
    """API AJAX qui reçoit une image et renvoie les résultats d'analyse en JSON."""
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'Aucune image fournie'}, status=400)

    uploaded_file = request.FILES['image']

    # Validation de la taille
    if uploaded_file.size > MAX_FILE_SIZE:
        return JsonResponse(
            {'error': 'Fichier trop volumineux (maximum 10 Mo)'},
            status=400
        )

    # Validation de l'extension
    name = uploaded_file.name.lower()
    ext = name.rsplit('.', 1)[-1] if '.' in name else ''
    if ext not in ACCEPTED_FORMATS:
        return JsonResponse(
            {'error': 'Format non accepté. Utilisez JPG, PNG ou WEBP.'},
            status=400
        )

    # Lecture de la transparence
    try:
        alpha = float(request.POST.get('alpha', 0.45))
        alpha = max(0.1, min(0.9, alpha))
    except (TypeError, ValueError):
        alpha = 0.45

    # Analyse
    try:
        pil_image = Image.open(uploaded_file)
        result = analyze_image(pil_image, alpha=alpha)
        result['success'] = True
        return JsonResponse(result)
    except Exception as exc:
        return JsonResponse(
            {'error': f'Erreur lors du traitement : {str(exc)}'},
            status=500
        )
