# 🌱 PhytoScan AI — Détection de Maladies des Plantes

Plateforme web de **détection de maladies des plantes** utilisant un modèle U-Net entraîné (segmentation sémantique). 

**🚀 Déployée en production sur Render** : https://phytoscan-0fva.onrender.com

---

## 📋 Caractéristiques

- ✅ **Détection U-Net** : Segmentation sémantique optimisée (ONNX Runtime)
- ✅ **ChatBot IA** : Assistant conversationnel avec support vocal (API Groq)
- ✅ **Interface Django** : Architecture modulaire avec 3 applications séparées
- ✅ **Responsive Design** : Mobile-first avec CSS moderne
- ✅ **Production-Ready** : Déployé sur Render, optimisé pour mémoire limitée

---

## 🏗️ Architecture du Projet

```
phytoscan/
│
├── 📄 manage.py                 # Point d'entrée Django
├── 📄 requirements.txt           # Dépendances Python (ONNX Runtime)
├── 📄 requirements-onnx.txt      # Dépendances sans PyTorch (pour Render)
├── 📄 .env.example               # Variables d'environnement
├── 📄 build.sh                   # Script de build Render (conversion ONNX)
├── 📄 convert_to_onnx.py         # Script de conversion PyTorch → ONNX (local)
├── 📄 ONNX_SETUP.md              # Guide migration ONNX
│
├── 📁 phytoscan/                 # Configuration Django
│   ├── settings.py               # ⚙️ Sécurité, BD, static files
│   ├── urls.py                   # Routage global
│   └── wsgi.py                   # Serveur WSGI/Gunicorn
│
├── 📁 core/                      # 🏠 Pages statiques (accueil, à propos, FAQ...)
│   ├── views.py
│   ├── forms.py                  # Formulaire de contact
│   ├── urls.py
│   └── templates/core/
│       ├── home.html
│       ├── features.html
│       ├── about.html
│       ├── faq.html
│       └── contact.html
│
├── 📁 detection/                 # 🔍 Détection d'images (U-Net ONNX)
│   ├── unet_model.py             # Inférence ONNX Runtime
│   ├── unet_model_onnx.py        # Version optimisée ONNX
│   ├── views.py                  # Endpoint API AJAX
│   ├── urls.py
│   ├── models/
│   │   ├── unet_best.onnx        # Modèle ONNX (~150 MB, téléchargé au build)
│   │   └── .gitignore            # ← Fichier modèle pas en Git
│   └── templates/detection/
│       └── detection.html
│
├── 📁 chatbot/                   # 🤖 Assistant IA (Groq API)
│   ├── views.py                  # Proxy sécurisé API
│   ├── urls.py
│   └── templates/chatbot/
│       └── widget.html           # Widget flottant
│
├── 📁 templates/
│   └── base.html                 # Template de base
│
└── 📁 static/
    ├── css/
    │   ├── style.css
    │   └── chatbot.css
    ├── js/
    │   ├── main.js
    │   ├── detection.js
    │   └── chatbot.js
    └── img/                      # Ressources images
```

---

## 🚀 Déploiement sur Render

### ✅ Configuration Actuelle

- **Plan** : Free (512 MB RAM)
- **Python** : 3.11.9
- **Runtime** : ONNX Runtime (au lieu de PyTorch)
- **Build** : ~8-10 min (conversion ONNX automatique)

### 📦 Optimisations Mémoire

| Composant | Avant | Après | Gain |
|-----------|-------|-------|------|
| **PyTorch** | 390 MB | - | - |
| **Modèle U-Net** | 500 MB | - | - |
| **ONNX Runtime** | - | 50 MB | ✅ |
| **Modèle ONNX** | - | 150 MB | ✅ 99.9% ↓ |
| **RAM total au démarrage** | 500+ MB ❌ | 250-300 MB ✅ | **50% économie** |

### 🔧 Processus de Build (Render)

1. Clone du repo (~8 MB, nettoyé)
2. Installation de `onnxruntime` (pas de PyTorch!)
3. **Conversion PyTorch → ONNX** (build.sh)
   - Télécharge modèle PyTorch depuis Google Drive
   - Convertit en ONNX (~5 min)
   - Supprime modèle PyTorch
4. Django démarre avec ONNX (~250 MB RAM)
5. ✅ Site live

### 🔗 Variables d'Environnement (à configurer dans Render Dashboard)

```bash
SECRET_KEY=<généré par Render>
DEBUG=False
GROQ_API_KEY=<votre clé Groq gratuite>
DATABASE_URL=<lié à base PostgreSQL>
```

---

## 💻 Installation Locale

### Prérequis

- Python 3.11+
- Git

### Étapes

**1. Cloner et créer venv**

```bash
git clone https://github.com/awa-gueye/D-tection-de-maladies-chez-les-plantes-avec-U-Net.git
cd D-tection-de-maladies-chez-les-plantes-avec-U-Net

python -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows
```

**2. Installer dépendances**

```bash
pip install -r requirements.txt
```

**3. Configuration .env**

```bash
cp .env.example .env
# Éditez .env avec votre clé Groq (gratuite sur https://console.groq.com)
```

**4. Base de données**

```bash
python manage.py migrate
python manage.py createsuperuser  # Optionnel
```

**5. Lancer le serveur**

```bash
python manage.py runserver
# Visitez http://localhost:8000
```

---

## 🤖 Modèle U-Net

### Architecture

- **Encoder** : ResNet50 (features pré-entraînées)
- **Decoder** : Convolutions transposées + skip connections
- **Output** : Segmentation binaire (sain vs malade)

### Performances

- **Epoch** : Trainé jusqu'à convergence
- **Validation IoU** : ~0.78 (bon compromise)
- **Temps inférence** : 50-100ms (ONNX Runtime)

### Fichiers

- **Entraînement** : `detection/models/unet_best.pth` (PyTorch)
- **Production** : `detection/models/unet_best.onnx` (ONNX, ~150 MB)
  - Généré automatiquement durant build Render
  - Pas en Git (.gitignore)
- **Données d'entraînement** : [📁 Google Drive](https://drive.google.com/drive/folders/1zw-zpzRiAuQElYnDsRgDzFtwYUBu4lyc?usp=sharing)
- **Notebook d'entraînement** : [📓 Google Colab](https://colab.research.google.com/drive/1y5Pf1KgdRJXLcPgGJ3t4TByQEGnb54xV#scrollTo=A0nYa2WbBfuc)

---

## 🔄 Migration ONNX (pour développeurs)

Si vous modifiez le modèle localement :

```bash
# 1. Mettre à jour le modèle PyTorch

# 2. Convertir en ONNX (local)
python convert_to_onnx.py

# 3. Vérifier la taille
ls -lh detection/models/unet_best.onnx

# 4. Push sur GitHub (fichier ONNX est dans .gitignore)
git add -A
git commit -m "Update model"
git push

# 5. Render reconvertira automatiquement au prochain deploy
```

---

## 📡 APIs

### Détection d'images

**Endpoint** : `POST /detection/api/analyze/`

**Paramètres** :
```json
{
  "image": <fichier multipart>,
  "alpha": 0.45
}
```

**Réponse** :
```json
{
  "predicted_class": "Plante saine",
  "predicted_state": "healthy",
  "disease_pct": 5.2,
  "healthy_pct": 94.8,
  "original_image": "data:image/png;base64,...",
  "mask_image": "data:image/png;base64,...",
  "overlay_image": "data:image/png;base64,...",
  "confidence": {
    "Plante saine": 95,
    "Maladie foliaire": 5,
    "Arrière-plan": 0
  },
  "model_mode": "real"
}
```

### ChatBot (Groq API)

Voir `chatbot/views.py` pour la configuration du proxy sécurisé.

---

## ⚙️ Configuration Django

### Fichiers Statiques

- **Local** : WhiteNoise (serveur dev)
- **Production** : WhiteNoise + gzip (Render)
- **Storage** : `StaticFilesStorage` (pas de compression pour économiser RAM)

### Base de Données

- **Local** : SQLite (`db.sqlite3`)
- **Production** : PostgreSQL (Render)

### Sécurité

- **SECURE_PROXY_SSL_HEADER** : ✅ Pour HTTPS sur Render
- **CSRF_COOKIE_SECURE** : ✅ En production
- **X_FRAME_OPTIONS** : `SAMEORIGIN` (autorise les iframes du même domaine)

---

## 🐛 Troubleshooting

### Error: "Ran out of memory on Render"

✅ **Résolu** : Migration vers ONNX Runtime
- Réduisez `--workers 1` dans `render.yaml`
- Augmentez `--timeout 300`

### Error: "No module named 'onnxruntime'"

```bash
pip install onnxruntime
```

### Modèle "Mode Démo" activé (image grise avec masque aléatoire)

1. Vérifiez que `detection/models/unet_best.onnx` existe
2. Consultez logs Render pour les erreurs

### Comment relancer le build Render?

Render → Dashboard → Service → "Rerun Last Deploy"

---

## 📝 Licence

MIT

---

## 👨‍💻 Développement

### Commandes utiles

```bash
# Lancer les tests
python manage.py test

# Collecte les fichiers statiques (dev)
python manage.py collectstatic --noinput

# Shell Django interactif
python manage.py shell

# Faire des migrations
python manage.py makemigrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Vider la BD
python manage.py flush
```

### Stack technologique

- **Backend** : Django 4.2
- **Frontend** : HTML5 + CSS3 + Vanilla JS
- **ML** : ONNX Runtime (inférence) + Segmentation Models PyTorch (entraînement)
- **Deployment** : Render (PaaS), PostgreSQL (BD)
- **Auth** : Django Auth + Groq API (chatbot)

---

## 📞 Support

Pour toute question sur le déploiement ou la configuration :
1. Consultez `ONNX_SETUP.md` (guide migration ONNX)
2. Vérifiez les logs Render
3. Lisez les commentaires dans `build.sh` et `unet_model.py`

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
