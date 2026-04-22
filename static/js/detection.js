/**
 * PhytoScan AI — Page de détection
 * Upload AJAX, prévisualisation et rendu des résultats
 */

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('detectionForm');
  if (!form) return;

  const fileInput = form.querySelector('input[type="file"]');
  const alphaSlider = form.querySelector('#alphaSlider');
  const alphaValue = form.querySelector('#alphaValue');
  const submitBtn = form.querySelector('button[type="submit"]');
  const resultWrap = document.getElementById('resultWrap');
  const placeholder = document.getElementById('resultPlaceholder');

  // Affichage dynamique de la valeur alpha
  if (alphaSlider && alphaValue) {
    alphaSlider.addEventListener('input', () => {
      alphaValue.textContent = parseFloat(alphaSlider.value).toFixed(2);
    });
  }

  function showLoading() {
    resultWrap.style.display = 'block';
    placeholder.style.display = 'none';
    resultWrap.innerHTML = `
      <div class="result-loading">
        <div class="spinner"></div>
        <p>Analyse en cours...</p>
      </div>
    `;
  }

  function showError(msg) {
    resultWrap.style.display = 'block';
    placeholder.style.display = 'none';
    resultWrap.innerHTML = `
      <div class="alert alert-error" style="margin:0">${msg}</div>
    `;
  }

  function showResult(data) {
    const badgeCls = data.predicted_state === 'diseased' ? 'badge-bad' : 'badge-ok';
    const bars = Object.entries(data.confidence).map(([label, value]) => `
      <div class="conf-row">
        <div class="conf-labels">
          <span>${label}</span>
          <span>${value}%</span>
        </div>
        <div class="conf-track">
          <div class="conf-fill" style="width:${value}%"></div>
        </div>
      </div>
    `).join('');

    resultWrap.style.display = 'block';
    placeholder.style.display = 'none';
    resultWrap.innerHTML = `
      <div class="result-box">
        <div class="result-head">
          <span class="result-head-title">Résultat de l'analyse</span>
          <span class="badge ${badgeCls}">${data.predicted_class}</span>
        </div>
        <div class="result-body">
          <div class="result-stats">
            <div class="result-stat healthy">
              <div class="result-stat-l">Surface saine</div>
              <div class="result-stat-v">${data.healthy_pct}%</div>
            </div>
            <div class="result-stat diseased">
              <div class="result-stat-l">Surface atteinte</div>
              <div class="result-stat-v">${data.disease_pct}%</div>
            </div>
          </div>
          <div class="conf-section-title">Niveau de confiance par classe</div>
          ${bars}
        </div>
      </div>
      <div class="result-images">
        <div class="result-img-wrap">
          <img src="${data.original_image}" alt="Originale">
          <div class="result-img-caption">Image originale</div>
        </div>
        <div class="result-img-wrap">
          <img src="${data.mask_image}" alt="Masque">
          <div class="result-img-caption">Masque U-Net</div>
        </div>
        <div class="result-img-wrap">
          <img src="${data.overlay_image}" alt="Superposition">
          <div class="result-img-caption">Superposition</div>
        </div>
      </div>
    `;
    // Animation progressive des barres
    requestAnimationFrame(() => {
      document.querySelectorAll('.conf-fill').forEach(fill => {
        fill.style.transition = 'width .8s cubic-bezier(.4,0,.2,1)';
      });
    });
  }

  form.addEventListener('submit', async function(e) {
    e.preventDefault();

    if (!fileInput.files.length) {
      showError('Veuillez sélectionner une image.');
      return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('alpha', alphaSlider ? alphaSlider.value : '0.45');

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    showLoading();
    submitBtn.disabled = true;
    submitBtn.innerText = 'Analyse...';

    try {
      const response = await fetch('/detection/api/analyze/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        body: formData,
      });
      const data = await response.json();
      if (response.ok && data.success) {
        showResult(data);
      } else {
        showError(data.error || 'Erreur lors de l\'analyse.');
      }
    } catch (err) {
      showError('Erreur de communication avec le serveur.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerText = 'Lancer l\'analyse';
    }
  });
});
