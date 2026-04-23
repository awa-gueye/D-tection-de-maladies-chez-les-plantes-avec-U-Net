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
// Carousel Équipe — fonctions globales (utilisées par onclick)
// Rotation automatique toutes les 10 secondes
// ═════════════════════════════════════════════════════
var teamCurrent = 0;
var teamInterval = null;

function teamGoTo(index) {
  var slides = document.querySelectorAll('.team-slide');
  var dots = document.querySelectorAll('.team-dot');
  if (!slides.length) return;

  slides.forEach(function(s) { s.classList.remove('active'); });
  dots.forEach(function(d) { d.classList.remove('active'); });

  teamCurrent = ((index % slides.length) + slides.length) % slides.length;
  slides[teamCurrent].classList.add('active');
  if (dots[teamCurrent]) dots[teamCurrent].classList.add('active');
}

function teamNext() {
  teamGoTo(teamCurrent + 1);
  teamResetAutoplay();
}

function teamPrev() {
  teamGoTo(teamCurrent - 1);
  teamResetAutoplay();
}

function teamResetAutoplay() {
  if (teamInterval) clearInterval(teamInterval);
  teamInterval = setInterval(function() { teamGoTo(teamCurrent + 1); }, 10000);
}

function toggleBio(index) {
  var bio = document.getElementById('teamBio' + index);
  if (bio) {
    bio.classList.toggle('expanded');
    var btn = bio.nextElementSibling;
    if (btn) {
      var isExpanded = bio.classList.contains('expanded');
      btn.innerHTML = isExpanded
        ? 'Réduire <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="18 15 12 9 6 15"/></svg>'
        : 'Lire la biographie complète <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>';
    }
  }
}

// Démarrer le carousel automatique
document.addEventListener('DOMContentLoaded', function() {
  var teamSlides = document.querySelectorAll('.team-slide');
  if (teamSlides.length > 1) {
    teamInterval = setInterval(function() { teamGoTo(teamCurrent + 1); }, 10000);

    // Pause au survol
    var carousel = document.getElementById('teamCarousel');
    if (carousel) {
      carousel.addEventListener('mouseenter', function() {
        if (teamInterval) clearInterval(teamInterval);
      });
      carousel.addEventListener('mouseleave', function() {
        teamInterval = setInterval(function() { teamGoTo(teamCurrent + 1); }, 10000);
      });
    }
  }
});
