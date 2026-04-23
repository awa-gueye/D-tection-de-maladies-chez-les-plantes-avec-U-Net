"""Vues de l'application core — pages principales du site PhytoScan AI."""
from django.shortcuts import render
from django.contrib import messages
from .forms import ContactForm


# Espèces du dataset PlantVillage pour la page d'accueil
PLANT_SPECIES = [
    {
        'slug': 'tomato', 'name': 'Tomate', 'classes': 10,
        'description': 'Mildiou, Tache bactérienne, Virus mosaïque, Septoriose',
        'color': '#FFEBEE',
    },
    {
        'slug': 'corn', 'name': 'Maïs', 'classes': 4,
        'description': 'Cercosporose, Rouille commune, Brûlure foliaire',
        'color': '#FFF8E1',
    },
    {
        'slug': 'potato', 'name': 'Pomme de terre', 'classes': 3,
        'description': 'Mildiou précoce, Mildiou tardif, Saine',
        'color': '#EFEBE9',
    },
    {
        'slug': 'apple', 'name': 'Pommier', 'classes': 4,
        'description': 'Tavelure, Pourriture noire, Rouille du cèdre',
        'color': '#FFEBEE',
    },
    {
        'slug': 'grape', 'name': 'Vigne', 'classes': 4,
        'description': 'Pourriture noire, Esca, Tache foliaire',
        'color': '#EDE7F6',
    },
    {
        'slug': 'pepper', 'name': 'Poivron', 'classes': 2,
        'description': 'Tache bactérienne, Sain',
        'color': '#FFF3E0',
    },
    {
        'slug': 'strawberry', 'name': 'Fraisier', 'classes': 2,
        'description': 'Brûlure des feuilles, Sain',
        'color': '#FCE4EC',
    },
    {
        'slug': 'cherry', 'name': 'Cerisier', 'classes': 2,
        'description': 'Oïdium, Sain',
        'color': '#FCE4EC',
    },
]

HOME_STATS = [
    {'value': '94,3%', 'label': 'Précision globale'},
    {'value': '38', 'label': 'Classes foliaires'},
    {'value': '54 305', 'label': 'Images d\'entraînement'},
    {'value': '0,912', 'label': 'Score IoU moyen'},
]

SLIDER = [
    {
        'tag': 'Deep Learning · Architecture U-Net · Dataset PlantVillage',
        'title': 'Détectez les maladies avant qu\'elles ne se propagent',
        'desc': 'Une solution d\'intelligence artificielle pour diagnostiquer précisément les infections foliaires et protéger vos cultures agricoles.',
        'bg': 'slide1.jpg',
        'grad': 'linear-gradient(135deg,#1B5E20,#33691E,#0A2E0D)',
        'buttons': [
            {'url': '/detection/', 'label': 'Analyser une image', 'cls': 'btn-gold'},
            {'url': '/a-propos/', 'label': 'En savoir plus', 'cls': 'btn-outline'},
        ]
    },
    {
        'tag': 'Dataset PlantVillage · 54 305 images annotées',
        'title': 'Un modèle entraîné sur la référence mondiale',
        'desc': 'Notre algorithme s\'appuie sur la plus grande base publique de phytopathologie, compilée par la Penn State University et maintenue sur Kaggle.',
        'bg': 'slide2.jpg',
        'grad': 'linear-gradient(135deg,#0D2B14,#1B5E20,#2E5E32)',
        'buttons': [
            {'url': '/dashboard/', 'label': 'Voir les métriques', 'cls': 'btn-gold'},
        ]
    },
    {
        'tag': 'Segmentation au pixel près',
        'title': 'Cartographiez exactement les zones atteintes',
        'desc': 'Le modèle U-Net génère un masque coloré qui distingue les tissus sains des zones infectées, avec un niveau de détail inégalé.',
        'bg': 'slide3.jpg',
        'grad': 'linear-gradient(135deg,#33691E,#558B2F,#1B3A0A)',
        'buttons': [
            {'url': '/fonctionnalites/', 'label': 'Voir les fonctionnalités', 'cls': 'btn-gold'},
        ]
    },
    {
        'tag': 'Précision 94,3% · IoU 0,912 · F1 0,935',
        'title': 'Des performances validées scientifiquement',
        'desc': 'Intervenez au bon moment, réduisez vos pertes jusqu\'à 40% et optimisez vos traitements phytosanitaires.',
        'bg': 'slide4.jpg',
        'grad': 'linear-gradient(135deg,#0A2E0D,#1B5E20,#2E7D32)',
        'buttons': [
            {'url': '/detection/', 'label': 'Démarrer l\'analyse', 'cls': 'btn-gold'},
            {'url': '/contact/', 'label': 'Nous contacter', 'cls': 'btn-outline'},
        ]
    },
]

FEATURES = [
    {
        'icon': 'shield',
        'title': 'Segmentation U-Net',
        'desc': 'L\'architecture encodeur-décodeur symétrique avec skip connections garantit une localisation précise des zones infectées au niveau du pixel, en résolution 256 par 256.'
    },
    {
        'icon': 'activity',
        'title': 'Tableau de bord analytique',
        'desc': 'Suivez vos analyses dans le temps grâce aux courbes d\'entraînement, aux métriques IoU, F1 et Dice, ainsi qu\'à l\'historique complet des diagnostics réalisés.'
    },
    {
        'icon': 'grid',
        'title': 'Visualisation multi-couches',
        'desc': 'Chaque analyse produit trois rendus côte à côte : l\'image originale, le masque de segmentation coloré et la superposition avec une transparence ajustable en temps réel.'
    },
    {
        'icon': 'search',
        'title': '38 classes foliaires',
        'desc': 'Le modèle reconnaît les principales pathologies affectant la tomate, la pomme de terre, le maïs, le pommier, la vigne, le poivron, le fraisier et le cerisier.'
    },
    {
        'icon': 'chat',
        'title': 'PhytoBot — Assistant IA',
        'desc': 'Un assistant conversationnel propulsé par Groq et LLaMA 3.3, capable de traiter vos messages texte, vos dictées vocales et vos images avec un prompt système personnalisable.'
    },
    {
        'icon': 'file',
        'title': 'Rapport détaillé',
        'desc': 'Pour chaque analyse, PhytoScan AI produit la classe prédite, le niveau de confiance par catégorie, la surface atteinte en pourcentage et des recommandations de traitement adaptées.'
    },
    {
        'icon': 'api',
        'title': 'API REST documentée',
        'desc': 'Intégrez la segmentation directement dans vos applications métier via notre API REST. Chaque requête retourne un JSON complet comprenant le masque, les métriques et les recommandations.'
    },
    {
        'icon': 'users',
        'title': 'Espaces collaboratifs',
        'desc': 'Organisez votre équipe avec des rôles et des permissions granulaires. Partagez vos analyses, commentez les résultats et collaborez en temps réel sur vos cas d\'étude.'
    },
    {
        'icon': 'alert',
        'title': 'Alertes intelligentes',
        'desc': 'Configurez des seuils par culture et recevez des notifications par e-mail dès qu\'une maladie critique dépasse le niveau d\'alerte que vous avez défini.'
    },
]

METHODOLOGY = [
    {
        'title': 'Acquisition et préparation des données',
        'desc': 'La première étape consiste à télécharger le dataset PlantVillage depuis Kaggle, puis à l\'explorer statistiquement pour comprendre la distribution des classes. Nous générons ensuite les masques de vérité terrain par binarisation HSV, suivie d\'un raffinement manuel. Le dataset est finalement partitionné en trois sous-ensembles : 70% pour l\'entraînement, 15% pour la validation et 15% pour le test final.'
    },
    {
        'title': 'Augmentation de données',
        'desc': 'Pour améliorer la capacité de généralisation du modèle, nous appliquons plusieurs transformations géométriques et photométriques : rotations jusqu\'à trente degrés, symétries horizontales et verticales, variations de zoom entre 0,8x et 1,2x, ainsi que des modifications de luminosité et de contraste pouvant atteindre vingt pour cent.'
    },
    {
        'title': 'Architecture U-Net',
        'desc': 'L\'implémentation s\'appuie sur Keras et TensorFlow. Nous utilisons une architecture à quatre niveaux encodeur-décodeur avec batch normalization et un dropout régularisé à 0,3. Les skip connections entre les couches symétriques permettent de préserver les informations spatiales fines perdues lors du sous-échantillonnage.'
    },
    {
        'title': 'Entraînement et optimisation',
        'desc': 'Nous utilisons l\'optimiseur Adam avec un taux d\'apprentissage initial de 1e-4 et une fonction de perte combinée BCE plus Dice Loss pour gérer efficacement le déséquilibre entre les classes. Les callbacks EarlyStopping et ReduceLROnPlateau surveillent la validation et ajustent dynamiquement l\'entraînement.'
    },
    {
        'title': 'Évaluation et déploiement',
        'desc': 'Le modèle final est évalué selon plusieurs métriques complémentaires sur le jeu de test : IoU, F1-Score, Precision, Recall, Pixel Accuracy et coefficient de Dice. Il est ensuite déployé via Django avec une interface utilisateur professionnelle enrichie d\'un assistant conversationnel propulsé par l\'API Groq.'
    },
]

FAQ_ITEMS = [
    {
        'q': 'Sur quel dataset le modèle a-t-il été entraîné ?',
        'a': 'PhytoScan AI est entraîné sur le dataset PlantVillage disponible sur Kaggle, plus précisément la version maintenue par Abdallah Ali Dev. Cette base rassemble 54 305 images de feuilles réparties sur 14 espèces cultivées et 38 classes combinant feuilles saines et maladies. Toutes les images ont été capturées en conditions contrôlées avec une résolution standard, ce qui garantit la cohérence de l\'entraînement.'
    },
    {
        'q': 'Quelles cultures et maladies sont reconnues ?',
        'a': 'Le modèle couvre 14 espèces : tomate (10 classes), pomme de terre (3), maïs (4), pommier (4), vigne (4), poivron (2), fraisier (2), cerisier (2), ainsi que le pêcher, le soja, la courge, le framboisier, le myrtillier et l\'oranger. Les pathologies reconnues incluent les mildious précoces et tardifs, les rouilles, les taches bactériennes, les viroses et les oïdiums.'
    },
    {
        'q': 'Quelle est la précision du modèle ?',
        'a': 'Sur le jeu de test PlantVillage, le modèle atteint une précision globale de 94,3%, un IoU moyen de 0,912, un F1-Score de 0,935 et un coefficient de Dice de 0,924. Les performances varient légèrement selon l\'espèce et la maladie considérées. Vous pouvez consulter le détail complet par classe dans la page Dashboard.'
    },
    {
        'q': 'Pourquoi utiliser U-Net plutôt qu\'un CNN classique ?',
        'a': 'Un CNN classique se contente de classer l\'image entière comme saine ou malade. U-Net va beaucoup plus loin en produisant un masque pixel par pixel qui localise précisément les zones infectées. Cette segmentation fine permet de quantifier la surface atteinte et de guider des traitements ciblés. U-Net excelle également sur les jeux de données de taille modérée.'
    },
    {
        'q': 'Mes images sont-elles stockées sur vos serveurs ?',
        'a': 'Absolument pas. Les images que vous téléversez sont traitées exclusivement en mémoire vive pendant la durée de l\'inférence et ne sont jamais sauvegardées de façon permanente sur disque. Votre confidentialité est totalement préservée et aucune donnée ne quitte votre session.'
    },
    {
        'q': 'Quel format et quelle résolution d\'image sont acceptés ?',
        'a': 'Les formats acceptés sont JPG, JPEG, PNG et WEBP, avec une taille maximale de dix mégaoctets par image. Pour un résultat optimal, nous recommandons une résolution minimale de 512 par 512 pixels. Les images sont automatiquement redimensionnées en 256 par 256 pixels avant d\'être soumises au modèle d\'inférence.'
    },
    {
        'q': 'Comment configurer le chatbot PhytoBot ?',
        'a': 'PhytoBot utilise l\'API Groq qui propose un usage gratuit généreux. Créez un compte sur console.groq.com, copiez votre clé API qui commence par gsk_, puis ajoutez-la dans le fichier .env à la ligne GROQ_API_KEY. Le chatbot supporte les messages vocaux sur Chrome et Edge, l\'upload d\'images et un prompt système personnalisable.'
    },
    {
        'q': 'Comment intégrer mon propre modèle U-Net ?',
        'a': 'Dans le fichier detection/unet_model.py, remplacez la fonction load_model par une implémentation qui charge votre fichier .h5 Keras. Le fichier doit produire un masque 256 par 256 en sortie. Le mode démonstration s\'efface automatiquement dès qu\'un modèle réel est détecté.'
    },
]



TEAM_MEMBERS = [
    {
        'name': 'Awa GUEYE',
        'role': 'Chef de projet & Data Scientist',
        'skills': 'Machine Learning, Deep Learning, Computer Vision',
        'bio': 'Étudiante en Licence Mathématiques-Statistiques-Économie option Data Science à l\'ENSAE Dakar. Passionnée par l\'intelligence artificielle appliquée au développement durable en Afrique. Responsable de l\'architecture U-Net et du pipeline d\'entraînement du modèle.',
        'image': 'team_awa.jpg',
    },
    {
        'name': 'Fatou Soumaya WADE',
        'role': 'Ingénieure Machine Learning',
        'skills': 'TensorFlow, Keras, Augmentation de données',
        'bio': 'Spécialiste en réseaux de neurones convolutifs et en techniques d\'augmentation de données. Responsable de l\'optimisation des hyperparamètres et de l\'évaluation des performances du modèle U-Net sur le dataset PlantVillage.',
        'image': 'team_fatou.jpg',
    },
    {
        'name': 'Ndeye Khary SALL',
        'role': 'Développeuse Full Stack',
        'skills': 'Django, JavaScript, Design UI/UX',
        'bio': 'Experte en développement web avec une attention particulière portée à l\'expérience utilisateur. Responsable de l\'interface frontend, du chatbot PhytoBot et du déploiement de la plateforme sur Render.',
        'image': 'team_khary.jpg',
    },
    {
        'name': 'Emmanuel DOSSEKOU',
        'role': 'Analyste de données & QA',
        'skills': 'Analyse statistique, Visualisation, Tests',
        'bio': 'Spécialiste en analyse exploratoire et en visualisation de données. Responsable du tableau de bord analytique, des métriques de performance et de l\'assurance qualité de l\'ensemble de la plateforme.',
        'image': 'team_emmanuel.jpg',
    },
]

def home(request):
    context = {
        'stats': HOME_STATS,
        'species': PLANT_SPECIES,
        'slider': SLIDER,
        'team': TEAM_MEMBERS,
    }
    return render(request, 'core/home.html', context)


def features(request):
    return render(request, 'core/features.html', {'features': FEATURES})


def about(request):
    return render(request, 'core/about.html', {'methodology': METHODOLOGY})


def faq(request):
    return render(request, 'core/faq.html', {'faq_items': FAQ_ITEMS})


def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Dans un environnement de production, envoyer l'email ici
            messages.success(
                request,
                'Votre message a été envoyé avec succès. Nous vous répondrons sous 24 heures.'
            )
            form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})


def dashboard(request):
    # Données simulées pour le dashboard
    metrics = {
        'total_analyses': '1 247',
        'precision': '94,3%',
        'diseases_detected': '312',
        'iou_score': '0,912',
    }
    detailed_metrics = [
        {'name': 'Precision', 'global': '0,943', 'healthy': '0,971', 'diseased': '0,889'},
        {'name': 'Recall', 'global': '0,927', 'healthy': '0,958', 'diseased': '0,876'},
        {'name': 'F1-Score', 'global': '0,935', 'healthy': '0,964', 'diseased': '0,882'},
        {'name': 'IoU', 'global': '0,912', 'healthy': '0,943', 'diseased': '0,854'},
        {'name': 'Pixel Accuracy', 'global': '0,961', 'healthy': '—', 'diseased': '—'},
        {'name': 'Dice', 'global': '0,924', 'healthy': '—', 'diseased': '—'},
    ]
    recent_analyses = [
        {'file': 'tomato_001.jpg', 'status': 'Malade', 'confidence': '94,1%', 'diagnosis': 'Mildiou tardif'},
        {'file': 'corn_045.jpg', 'status': 'Saine', 'confidence': '98,7%', 'diagnosis': '—'},
        {'file': 'potato_023.jpg', 'status': 'Malade', 'confidence': '87,6%', 'diagnosis': 'Mildiou précoce'},
        {'file': 'apple_112.jpg', 'status': 'Saine', 'confidence': '96,2%', 'diagnosis': '—'},
        {'file': 'grape_078.jpg', 'status': 'Malade', 'confidence': '91,3%', 'diagnosis': 'Pourriture noire'},
    ]
    class_performance = [
        {'name': 'Sain', 'iou': 0.943},
        {'name': 'Mildiou précoce', 'iou': 0.889},
        {'name': 'Mildiou tardif', 'iou': 0.912},
        {'name': 'Rouille', 'iou': 0.878},
        {'name': 'Tache bactérienne', 'iou': 0.905},
        {'name': 'Oïdium', 'iou': 0.931},
    ]
    context = {
        'metrics': metrics,
        'detailed_metrics': detailed_metrics,
        'recent_analyses': recent_analyses,
        'class_performance': class_performance,
    }
    return render(request, 'core/dashboard.html', context)
