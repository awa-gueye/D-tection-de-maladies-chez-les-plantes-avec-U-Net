/**
 * PhytoScan AI — JavaScript principal
 * Slider, FAQ accordéon, menu mobile
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
      slides.forEach(s => s.classList.remove('active'));
      dots.forEach(d => d.classList.remove('active'));
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

    dots.forEach((dot, i) => {
      dot.addEventListener('click', () => {
        stopAutoplay();
        goToSlide(i);
        startAutoplay();
      });
    });

    // Pause au survol
    const sliderWrap = document.querySelector('.slider-wrap');
    if (sliderWrap) {
      sliderWrap.addEventListener('mouseenter', stopAutoplay);
      sliderWrap.addEventListener('mouseleave', startAutoplay);
    }

    startAutoplay();
  }

  // ═════════════════════════════════════════════════
  // FAQ accordéon
  // ═════════════════════════════════════════════════
  document.querySelectorAll('.faq-q').forEach(button => {
    button.addEventListener('click', function() {
      const item = this.closest('.faq-item');
      if (item) {
        item.classList.toggle('open');
      }
    });
  });

  // ═════════════════════════════════════════════════
  // Menu mobile
  // ═════════════════════════════════════════════════
  const mobileToggle = document.querySelector('.navbar-mobile-toggle');
  const navLinks = document.querySelector('.navbar-links');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', function() {
      navLinks.classList.toggle('open');
    });
    // Ferme le menu après clic sur un lien
    navLinks.querySelectorAll('.navbar-link').forEach(link => {
      link.addEventListener('click', () => navLinks.classList.remove('open'));
    });
  }

  // ═════════════════════════════════════════════════
  // Smooth scroll sur les liens d'ancre
  // ═════════════════════════════════════════════════
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});
