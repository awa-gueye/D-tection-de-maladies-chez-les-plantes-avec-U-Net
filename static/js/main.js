/**
 * PhytoScan AI — JavaScript principal
 * Slider hero, FAQ accordéon, menu mobile, carousel équipe, animations scroll
 */

document.addEventListener('DOMContentLoaded', function() {

  // ═════════════════════════════════════════════════
  // Slider hero — défilement automatique + dots
  // ═════════════════════════════════════════════════
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.slider-dot');
  if (slides.length > 1) {
    let currentSlide = 0;
    let slideInterval;

    function goToSlide(index) {
      slides.forEach(function(s) { s.classList.remove('active'); });
      dots.forEach(function(d) { d.classList.remove('active'); });
      slides[index].classList.add('active');
      if (dots[index]) dots[index].classList.add('active');
      currentSlide = index;
    }

    function nextSlide() {
      goToSlide((currentSlide + 1) % slides.length);
    }

    function startAutoplay() {
      slideInterval = setInterval(nextSlide, 6000);
    }

    function stopAutoplay() {
      clearInterval(slideInterval);
    }

    dots.forEach(function(dot, i) {
      dot.addEventListener('click', function() {
        stopAutoplay();
        goToSlide(i);
        startAutoplay();
      });
    });

    var sliderWrap = document.querySelector('.slider-wrap');
    if (sliderWrap) {
      sliderWrap.addEventListener('mouseenter', stopAutoplay);
      sliderWrap.addEventListener('mouseleave', startAutoplay);
    }

    startAutoplay();
  }

  // ═════════════════════════════════════════════════
  // FAQ accordéon
  // ═════════════════════════════════════════════════
  document.querySelectorAll('.faq-q').forEach(function(button) {
    button.addEventListener('click', function() {
      var item = this.closest('.faq-item');
      if (item) {
        item.classList.toggle('open');
      }
    });
  });

  // ═════════════════════════════════════════════════
  // Menu mobile
  // ═════════════════════════════════════════════════
  var mobileToggle = document.querySelector('.navbar-mobile-toggle');
  var navLinks = document.querySelector('.navbar-links');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', function() {
      navLinks.classList.toggle('open');
    });
    navLinks.querySelectorAll('.navbar-link').forEach(function(link) {
      link.addEventListener('click', function() {
        navLinks.classList.remove('open');
      });
    });
  }

  // ═════════════════════════════════════════════════
  // Animations au scroll (Intersection Observer)
  // ═════════════════════════════════════════════════
  var animateElements = document.querySelectorAll('.animate-on-scroll, .card, .plant-card, .kpi, .cinfo-card, .dataset-tile, .tl-item, .faq-item');
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    animateElements.forEach(function(el) {
      observer.observe(el);
    });
  }

  // ═════════════════════════════════════════════════
  // Smooth scroll
  // ═════════════════════════════════════════════════
  document.querySelectorAll('a[href^="#"]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});

// ═════════════════════════════════════════════════════
// Carousel Équipe — version robuste avec autoplay
// ═════════════════════════════════════════════════════
(function() {
  let teamCurrent = 0;
  let teamInterval = null;
  let teamSlides, teamDots;
  const AUTOPLAY_DELAY = 8000; // 8 secondes

  function updateTeamSlide(index) {
    if (!teamSlides || !teamDots) return;
    teamSlides.forEach((slide, i) => {
      slide.classList.toggle('active', i === index);
    });
    teamDots.forEach((dot, i) => {
      dot.classList.toggle('active', i === index);
    });
    teamCurrent = index;
  }

  function teamGoTo(index) {
    if (!teamSlides.length) return;
    let newIndex = (index % teamSlides.length + teamSlides.length) % teamSlides.length;
    updateTeamSlide(newIndex);
    teamResetAutoplay();
  }

  function teamNext() {
    teamGoTo(teamCurrent + 1);
  }

  function teamPrev() {
    teamGoTo(teamCurrent - 1);
  }

  function teamResetAutoplay() {
    if (teamInterval) clearInterval(teamInterval);
    teamInterval = setInterval(() => {
      teamGoTo(teamCurrent + 1);
    }, AUTOPLAY_DELAY);
  }

  function stopAutoplay() {
    if (teamInterval) clearInterval(teamInterval);
    teamInterval = null;
  }

  // Exposition globale (nécessaire car les onclick du HTML les appellent)
  window.teamGoTo = teamGoTo;
  window.teamNext = teamNext;
  window.teamPrev = teamPrev;

  // Initialisation
  document.addEventListener('DOMContentLoaded', function() {
    teamSlides = document.querySelectorAll('.team-slide');
    teamDots = document.querySelectorAll('.team-dot');
    if (teamSlides.length <= 1) return;

    // Sélectionner le slide actif
    teamSlides.forEach((slide, idx) => {
      if (slide.classList.contains('active')) teamCurrent = idx;
    });

    // Attacher événements aux flèches
    const prevBtn = document.querySelector('.team-nav-prev');
    const nextBtn = document.querySelector('.team-nav-next');
    if (prevBtn) prevBtn.addEventListener('click', teamPrev);
    if (nextBtn) nextBtn.addEventListener('click', teamNext);

    // Attacher événements aux dots
    teamDots.forEach((dot, idx) => {
      dot.addEventListener('click', () => teamGoTo(idx));
    });

    // Autoplay avec pause au survol
    const carousel = document.getElementById('teamCarousel');
    if (carousel) {
      carousel.addEventListener('mouseenter', stopAutoplay);
      carousel.addEventListener('mouseleave', teamResetAutoplay);
    }
    teamResetAutoplay();
  });
})();

// Gestion des biographies (toggle + icône adaptée)
function toggleBio(bioId) {
  const bioPara = document.getElementById(`teamBio${bioId}`);
  if (!bioPara) return;
  const btn = bioPara.closest('.team-slide').querySelector('.team-bio-btn');
  const isExpanded = bioPara.classList.contains('expanded');
  
  if (!isExpanded) {
    bioPara.classList.add('expanded');
    bioPara.style.maxHeight = bioPara.scrollHeight + 'px';
    btn.innerHTML = `Réduire la biographie
      <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="5" y1="12" x2="19" y2="12"/>
      </svg>`;
  } else {
    bioPara.classList.remove('expanded');
    bioPara.style.maxHeight = '';
    btn.innerHTML = `Lire la biographie complète
      <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="5" y1="12" x2="19" y2="12"/>
        <polyline points="12 5 19 12 12 19"/>
      </svg>`;
  }
}

// Attacher les événements aux boutons de bio après le chargement du DOM
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.team-bio-btn').forEach(btn => {
    const bioId = btn.getAttribute('data-bio-id');
    if (bioId !== null) {
      btn.removeEventListener('click', () => toggleBio(bioId));
      btn.addEventListener('click', () => toggleBio(parseInt(bioId)));
    }
  });
});