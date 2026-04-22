/**
 * PhytoScan AI — Chatbot PhytoBot
 * - Communication via proxy Django sécurisé (clé API côté serveur)
 * - Messages vocaux via Web Speech API (Chrome/Edge)
 * - Upload d'images avec LLaMA Vision
 * - Prompt système personnalisable
 */

(function() {
  'use strict';

  const DEFAULT_PROMPT = (
    "Tu es PhytoBot, assistant expert en phytopathologie et Deep Learning U-Net. " +
    "Tu aides les utilisateurs de PhytoScan AI, une plateforme de segmentation " +
    "sémantique basée sur le dataset PlantVillage (Kaggle, 54 305 images, " +
    "14 espèces, 38 maladies foliaires). Tu réponds en français, de manière " +
    "claire et concise (3 à 5 phrases). Tes domaines : maladies des plantes, " +
    "symptômes, diagnostic visuel, architecture U-Net, métriques IoU/F1/Dice, " +
    "conseils agronomiques."
  );

  let history = [];
  let isOpen = false;
  let attachedImage = null;
  let recognition = null;
  let isRecording = false;
  let currentPrompt = DEFAULT_PROMPT;

  // DOM refs (résolues après DOMContentLoaded)
  let fab, win, badge, msgsEl, inputEl, fileInput, previewEl, previewImg, previewName;
  let voiceBtn, promptPanel, promptInput, suggestionsEl;

  function $(sel, parent) {
    return (parent || document).querySelector(sel);
  }

  function currentTime() {
    return new Date().toLocaleTimeString('fr-FR', {
      hour: '2-digit', minute: '2-digit'
    });
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatMessage(text) {
    // Échappe puis convertit **gras**, `code` et retours à la ligne
    let html = escapeHtml(text);
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/\n/g, '<br>');
    return html;
  }

  function addMessage(text, role, imageSrc) {
    const el = document.createElement('div');
    el.className = 'chat-msg ' + role;
    let html = '';
    if (imageSrc) {
      html += '<img class="chat-msg-img" src="' + imageSrc + '">';
    }
    html += '<div class="chat-bubble">' + formatMessage(text) + '</div>';
    html += '<div class="chat-time">' + currentTime() + '</div>';
    el.innerHTML = html;
    msgsEl.appendChild(el);
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  function showTyping() {
    const el = document.createElement('div');
    el.id = 'chat-typing';
    el.className = 'chat-msg bot';
    el.innerHTML = (
      '<div class="chat-bubble">' +
      '<div class="chat-typing">' +
      '<span class="chat-typing-dot"></span>' +
      '<span class="chat-typing-dot"></span>' +
      '<span class="chat-typing-dot"></span>' +
      '</div></div>'
    );
    msgsEl.appendChild(el);
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  function hideTyping() {
    const el = document.getElementById('chat-typing');
    if (el) el.remove();
  }

  function toggleChat() {
    isOpen = !isOpen;
    win.classList.toggle('open', isOpen);
    if (isOpen) {
      badge.classList.remove('visible');
      setTimeout(() => inputEl.focus(), 200);
    }
  }

  function togglePrompt() {
    promptPanel.classList.toggle('open');
  }

  function savePrompt() {
    const v = promptInput.value.trim();
    currentPrompt = v || DEFAULT_PROMPT;
    addMessage('Prompt système mis à jour.', 'bot');
    togglePrompt();
  }

  function resetPrompt() {
    currentPrompt = DEFAULT_PROMPT;
    promptInput.value = DEFAULT_PROMPT;
    addMessage('Prompt système réinitialisé.', 'bot');
  }

  function quickAsk(text) {
    suggestionsEl.classList.add('hidden');
    inputEl.value = text;
    send();
  }

  function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      addMessage('Image trop volumineuse (maximum 10 Mo).', 'bot');
      return;
    }
    const reader = new FileReader();
    reader.onload = function(ev) {
      attachedImage = ev.target.result;
      previewImg.src = attachedImage;
      previewName.textContent = file.name;
      previewEl.classList.add('visible');
    };
    reader.readAsDataURL(file);
  }

  function removeImage() {
    attachedImage = null;
    previewEl.classList.remove('visible');
    fileInput.value = '';
  }

  function toggleVoice() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      addMessage(
        'Votre navigateur ne supporte pas la reconnaissance vocale. ' +
        'Essayez Chrome ou Edge.',
        'bot'
      );
      return;
    }
    if (isRecording && recognition) {
      recognition.stop();
      return;
    }
    recognition = new SR();
    recognition.lang = 'fr-FR';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = function() {
      voiceBtn.classList.add('recording');
      isRecording = true;
    };
    recognition.onresult = function(event) {
      const transcript = event.results[0][0].transcript;
      voiceBtn.classList.remove('recording');
      isRecording = false;
      inputEl.value = transcript;
      send();
    };
    recognition.onerror = function(event) {
      voiceBtn.classList.remove('recording');
      isRecording = false;
      if (event.error === 'not-allowed') {
        addMessage('Accès au microphone refusé. Autorisez-le dans les paramètres du navigateur.', 'bot');
      } else if (event.error !== 'no-speech') {
        addMessage('Erreur micro : ' + event.error, 'bot');
      }
    };
    recognition.onend = function() {
      voiceBtn.classList.remove('recording');
      isRecording = false;
    };
    try {
      recognition.start();
    } catch (e) {
      voiceBtn.classList.remove('recording');
      isRecording = false;
    }
  }

  async function send() {
    const text = inputEl.value.trim();
    if (!text && !attachedImage) return;

    const userImage = attachedImage;
    const displayText = text || '[Image envoyée]';
    inputEl.value = '';

    // Affiche le message utilisateur
    addMessage(displayText, 'user', userImage);
    suggestionsEl.classList.add('hidden');

    // Construction du payload à envoyer au serveur
    let userMessage;
    if (userImage) {
      userMessage = {
        role: 'user',
        content: [
          { type: 'text', text: text || 'Analyse cette image de feuille et identifie les éventuelles maladies.' },
          { type: 'image_url', image_url: { url: userImage } }
        ]
      };
    } else {
      userMessage = { role: 'user', content: text };
    }
    history.push(userMessage);

    removeImage();
    showTyping();

    // Récupération du CSRF token
    const csrfToken = getCookie('csrftoken') || getCSRFFromMeta();

    try {
      const response = await fetch('/chatbot/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || '',
        },
        body: JSON.stringify({
          messages: history,
          system_prompt: currentPrompt,
          has_image: !!userImage,
        })
      });
      const data = await response.json();
      hideTyping();

      if (response.ok && data.success) {
        addMessage(data.reply, 'bot');
        history.push({ role: 'assistant', content: data.reply });
        if (!isOpen) badge.classList.add('visible');
      } else if (response.status === 503) {
        addMessage(data.message, 'bot');
      } else {
        addMessage(data.message || 'Erreur : ' + (data.error || 'inconnue'), 'bot');
      }
    } catch (err) {
      hideTyping();
      addMessage('Erreur de connexion au serveur. Vérifiez votre connexion.', 'bot');
    }
  }

  function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [k, v] = cookie.trim().split('=');
      if (k === name) return decodeURIComponent(v);
    }
    return null;
  }

  function getCSRFFromMeta() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : null;
  }

  // ═════════════════════════════════════════════════
  // Initialisation
  // ═════════════════════════════════════════════════
  document.addEventListener('DOMContentLoaded', function() {
    fab = $('#chatFab');
    win = $('#chatWindow');
    badge = $('#chatBadge');
    msgsEl = $('#chatMessages');
    inputEl = $('#chatInput');
    fileInput = $('#chatFileInput');
    previewEl = $('#chatPreview');
    previewImg = $('#chatPreviewImg');
    previewName = $('#chatPreviewName');
    voiceBtn = $('#chatVoiceBtn');
    promptPanel = $('#chatPromptPanel');
    promptInput = $('#chatPromptInput');
    suggestionsEl = $('#chatSuggestions');

    if (!fab) return; // Chatbot désactivé sur cette page

    // Initialise le prompt
    promptInput.value = DEFAULT_PROMPT;

    // Event listeners
    fab.addEventListener('click', toggleChat);
    $('#chatCloseBtn').addEventListener('click', toggleChat);
    $('#chatPromptBtn').addEventListener('click', togglePrompt);
    $('#chatPromptSave').addEventListener('click', savePrompt);
    $('#chatPromptReset').addEventListener('click', resetPrompt);
    $('#chatFileBtn').addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleImageUpload);
    $('#chatPreviewRemove').addEventListener('click', removeImage);
    voiceBtn.addEventListener('click', toggleVoice);
    $('#chatSendBtn').addEventListener('click', send);
    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });

    // Suggestions rapides
    document.querySelectorAll('.chat-sug').forEach(btn => {
      btn.addEventListener('click', () => quickAsk(btn.dataset.q));
    });
  });
})();
