# PhytoScan AI — Django

Plateforme de détection de maladies des plantes par segmentation sémantique U-Net.
Architecture Django propre avec trois applications séparées, chatbot IA intégré
(voix, image, prompt personnalisable), et interface professionnelle en Times New Roman + Arial.

## Structure du projet

```
phytoscan_django/
│
├── manage.py                    # Point d'entrée Django
├── requirements.txt             # Dépendances Python
├── .env.example                 # Variables d'environnement (à copier en .env)
│
├── phytoscan/                   # Configuration du projet
│   ├── settings.py              # Configuration principale
│   ├── urls.py                  # Routage global
│   └── wsgi.py                  # Serveur WSGI
│
├── core/                        # App : pages principales (accueil, à propos, FAQ...)
│   ├── views.py                 # Contenu textuel et vues
│   ├── forms.py                 # Formulaire de contact
│   ├── urls.py
│   ├── context_processors.py    # Variables globales (nom du site, clé Groq...)
│   └── templates/core/
│       ├── home.html
│       ├── features.html
│       ├── about.html
│       ├── faq.html
│       ├── contact.html
│       └── dashboard.html
│
├── detection/                   # App : détection d'images
│   ├── unet_model.py            # Inférence U-Net (mode démo par défaut)
│   ├── views.py                 # Vue de la page + endpoint API AJAX
│   ├── urls.py
│   └── templates/detection/
│       └── detection.html
│
├── chatbot/                     # App : assistant IA PhytoBot
│   ├── views.py                 # Proxy sécurisé vers l'API Groq
│   ├── urls.py
│   └── templates/chatbot/
│       └── widget.html          # Widget flottant (inclus dans base.html)
│
├── templates/
│   └── base.html                # Template de base (navbar, footer, chatbot)
│
└── static/
    ├── css/
    │   ├── style.css            # Styles principaux (Times New Roman + Arial)
    │   └── chatbot.css          # Styles du chatbot
    ├── js/
    │   ├── main.js              # Slider, FAQ, menu mobile
    │   ├── detection.js         # Upload AJAX et rendu des résultats
    │   └── chatbot.js           # Voix, image, prompt, API proxy
    └── img/                     # Images statiques (slides, logos)
```

## Installation

**1. Cloner le projet et créer un environnement virtuel**

```bash
python -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows
```

**2. Installer les dépendances**

```bash
pip install -r requirements.txt
```

**3. Configurer les variables d'environnement**

Copiez le fichier d'exemple et modifiez-le :

```bash
cp .env.example .env
```

Éditez `.env` pour configurer votre clé Groq (gratuite sur https://console.groq.com) :

```
SECRET_KEY=generez-une-cle-longue-et-aleatoire
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GROQ_API_KEY=gsk_votre_cle_ici
```

**4. Initialiser la base de données**

```bash
python manage.py migrate
python manage.py createsuperuser    # Optionnel : pour l'interface admin
```

**5. Lancer le serveur de développement**

```bash
python manage.py runserver
```

Le site est accessible à http://127.0.0.1:8000/

## Fonctionnalités

### Pages publiques

- **Accueil** : slider animé (4 slides avec rotation automatique), statistiques, présentation
  de la mission, cartes des 8 espèces principales, dataset PlantVillage, CTA
- **Fonctionnalités** : 9 cartes détaillant les capacités de la plateforme
- **Détection** : upload d'image AJAX, slider de transparence, résultats avec segmentation
- **Dashboard** : KPI, courbes d'entraînement en SVG pur, distribution, historique
- **À propos** : histoire, méthodologie en timeline animée, valeurs
- **FAQ** : 8 questions avec accordéon animé
- **Contact** : formulaire validé côté serveur avec messages de succès

### Chatbot PhytoBot

- **Proxy sécurisé** : la clé Groq reste côté serveur, jamais exposée au navigateur
- **Messages texte** : LLaMA 3.3 70B (modèle puissant et rapide)
- **Messages vocaux** : Web Speech API en français (Chrome/Edge uniquement)
- **Upload d'images** : analyse visuelle avec LLaMA 3.2 Vision
- **Prompt système** : entièrement personnalisable via l'icône engrenage
- **Suggestions rapides** : 3 questions pré-remplies
- **Indicateur de frappe** : animation de points pendant la réponse
- **Notification** : badge si réponse reçue alors que le chat est fermé

### Design et typographie

- **Titres** : Times New Roman (serif classique et élégant)
- **Corps** : Arial (lisibilité optimale)
- **Palette** : verts naturels (#1B5E20, #2E7D32) et doré (#C8922A)
- **Animations CSS** : fadeUp, slideRight, scaleIn, pulse, recordPulse
- **Responsive** : adapté tablette et mobile avec menu hamburger

## Configuration de PhytoBot

1. Créez un compte gratuit sur https://console.groq.com
2. Copiez votre clé API (elle commence par `gsk_`)
3. Collez-la dans `.env` à la ligne `GROQ_API_KEY=`
4. Redémarrez le serveur Django

Sans clé configurée, un toast d'information discret apparaît en bas à gauche de la page.

## Intégrer votre propre modèle U-Net

Le fichier `detection/unet_model.py` fonctionne par défaut en **mode démonstration**
(masque simulé par binarisation HSV).

Pour connecter votre vrai modèle entraîné :

```python
# Dans detection/unet_model.py
MODEL = load_model(path='chemin/vers/votre_modele.h5')
```

Votre modèle Keras/TensorFlow doit :
- Accepter une entrée de forme `(1, 256, 256, 3)` normalisée entre 0 et 1
- Retourner un masque de forme `(256, 256, 1)` avec des valeurs entre 0 et 1

## Dataset utilisé

PlantVillage (Kaggle) : https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset

- 54 305 images de feuilles
- 14 espèces cultivées
- 38 classes (saines + malades)
- Résolution standard 256×256
- Compilé par Hughes & Salathé (Penn State University, 2015)

## Ajout de vos propres images

Placez vos images dans `static/img/` :

- `slide1.jpg` à `slide4.jpg` — slider d'accueil
- Vos logos et illustrations personnalisées

Après modification des fichiers statiques en production, exécutez :

```bash
python manage.py collectstatic
```

## Déploiement en production

**Variables à changer dans `.env` :**

```
DEBUG=False
ALLOWED_HOSTS=votredomaine.com,www.votredomaine.com
SECRET_KEY=cle-vraiment-aleatoire-et-longue
```

**Serveurs recommandés :** Gunicorn + Nginx, Render, Railway, Heroku, PythonAnywhere

**Avant le premier déploiement :**

```bash
python manage.py collectstatic --noinput
python manage.py migrate
```

## Licence

Projet académique à usage libre pour la recherche et l'enseignement.
