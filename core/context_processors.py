"""Processeurs de contexte pour injecter des variables globales dans tous les templates."""
from django.conf import settings


def site_context(request):
    """Variables disponibles dans tous les templates."""
    return {
        'SITE_NAME': 'PhytoScan AI',
        'SITE_TAGLINE': 'Détection de maladies des plantes par IA',
        'GROQ_API_KEY': settings.GROQ_API_KEY,
        'GROQ_CONFIGURED': bool(settings.GROQ_API_KEY),
        'DATASET_URL': 'https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset',
        'CURRENT_YEAR': 2025,
    }
