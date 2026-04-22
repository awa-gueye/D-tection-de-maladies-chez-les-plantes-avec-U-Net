"""Vues de l'application chatbot — proxy sécurisé vers l'API Groq.

La clé API reste côté serveur et n'est jamais exposée au navigateur.
"""
import json
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings

GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
MODEL_TEXT = 'llama-3.3-70b-versatile'
MODEL_VISION = 'llama-3.2-11b-vision-preview'

DEFAULT_SYSTEM_PROMPT = (
    "Tu es PhytoBot, assistant expert en phytopathologie et Deep Learning U-Net. "
    "Tu aides les utilisateurs de PhytoScan AI, une plateforme de segmentation "
    "sémantique basée sur le dataset PlantVillage (Kaggle, 54 305 images, "
    "14 espèces, 38 maladies foliaires). Tu réponds en français, de manière "
    "claire et concise (3 à 5 phrases). Tes domaines : maladies des plantes, "
    "symptômes, diagnostic visuel, architecture U-Net, métriques IoU/F1/Dice, "
    "conseils agronomiques et interprétation des résultats de segmentation."
)


@require_http_methods(['POST'])
def chat_endpoint(request):
    """Proxy sécurisé vers Groq. La clé API reste côté serveur."""
    if not settings.GROQ_API_KEY:
        return JsonResponse({
            'error': 'chatbot_non_configure',
            'message': (
                "Le chatbot n'est pas configuré. Ajoutez votre clé Groq "
                "dans le fichier .env à la ligne GROQ_API_KEY."
            )
        }, status=503)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)

    messages = payload.get('messages', [])
    system_prompt = payload.get('system_prompt', '').strip() or DEFAULT_SYSTEM_PROMPT
    has_image = payload.get('has_image', False)

    # Sélection du modèle adapté
    model = MODEL_VISION if has_image else MODEL_TEXT

    # Construction de la requête Groq
    full_messages = [{'role': 'system', 'content': system_prompt}] + messages

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                'Authorization': f'Bearer {settings.GROQ_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': model,
                'messages': full_messages,
                'max_tokens': 800,
                'temperature': 0.7,
            },
            timeout=30,
        )
    except requests.Timeout:
        return JsonResponse({'error': 'timeout', 'message': 'Délai dépassé.'}, status=504)
    except requests.RequestException as exc:
        return JsonResponse(
            {'error': 'connexion', 'message': f'Erreur de connexion : {exc}'},
            status=502
        )

    if response.status_code != 200:
        return JsonResponse({
            'error': 'api_error',
            'message': f'Erreur API ({response.status_code})',
            'details': response.text[:200],
        }, status=response.status_code)

    data = response.json()
    try:
        reply = data['choices'][0]['message']['content']
    except (KeyError, IndexError):
        return JsonResponse({
            'error': 'reponse_invalide',
            'message': 'Réponse API malformée.'
        }, status=500)

    return JsonResponse({
        'success': True,
        'reply': reply,
        'model': model,
    })
