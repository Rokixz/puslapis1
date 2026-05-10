// ===== MOBILE MENU TOGGLE =====
const toggle = document.getElementById('menuToggle');
const nav = document.getElementById('mainNav');

if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    toggle.classList.toggle('active');
    // Update ARIA attributes for accessibility
    toggle.setAttribute('aria-expanded', isOpen);
  });

  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.classList.remove('active');
      toggle.setAttribute('aria-expanded', false);
    });
  });

  // Close menu on escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('open')) {
      nav.classList.remove('open');
      toggle.classList.remove('active');
      toggle.setAttribute('aria-expanded', false);
    }
  });
}

// ===== SCROLL REVEAL & ANIMATIONS =====
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.service-card, .project-card, .team-card, .testimonial-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(24px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});

// ===== FORM VALIDATION & SUBMISSION =====
const contactForm = document.querySelector('form');
if (contactForm) {
  // Real-time validation
  const inputs = contactForm.querySelectorAll('input[required], textarea[required]');
  inputs.forEach(input => {
    input.addEventListener('blur', () => validateField(input));
    input.addEventListener('input', () => {
      if (input.classList.contains('invalid')) {
        validateField(input);
      }
    });
  });

  // Email validation
  const emailInput = contactForm.querySelector('input[type="email"]');
  if (emailInput) {
    emailInput.addEventListener('blur', () => {
      const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value);
      if (!isValid && emailInput.value) {
        emailInput.classList.add('invalid');
        showError(emailInput, 'Prašom įvesti validų el. pašto adresą');
      } else {
        emailInput.classList.remove('invalid');
        removeError(emailInput);
      }
    });
  }

  // Form submission
  contactForm.addEventListener('submit', (e) => {
    let isValid = true;
    inputs.forEach(input => {
      if (!validateField(input)) {
        isValid = false;
      }
    });

    if (!isValid) {
      e.preventDefault();
    } else {
      // Add loading state
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.textContent;
      submitBtn.textContent = 'Siuntimas...';
      submitBtn.disabled = true;

      // Reset after submission (Formspree handles this)
      setTimeout(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
      }, 2000);
    }
  });
}

function validateField(input) {
  const value = input.value.trim();
  
  if (input.type === 'email') {
    const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    if (!isValid && value) {
      input.classList.add('invalid');
      showError(input, 'Neteisingas el. paštas');
      return false;
    }
  } else if (input.required && !value) {
    input.classList.add('invalid');
    showError(input, 'Šis laukas yra privalomas');
    return false;
  }

  input.classList.remove('invalid');
  removeError(input);
  return true;
}

function showError(input, message) {
  let errorEl = input.nextElementSibling;
  if (!errorEl || !errorEl.classList.contains('error-message')) {
    errorEl = document.createElement('span');
    errorEl.className = 'error-message';
    input.parentNode.insertBefore(errorEl, input.nextSibling);
  }
  errorEl.textContent = message;
}

function removeError(input) {
  const errorEl = input.nextElementSibling;
  if (errorEl && errorEl.classList.contains('error-message')) {
    errorEl.remove();
  }
}

// ===== SLIDESHOW =====
(function() {
  const track = document.getElementById('slideshowTrack');
  if (!track) return;

  const slides = track.querySelectorAll('.slide');
  const dotsContainer = document.getElementById('slideDots');
  let current = 0;
  let timer;

  // Build dots
  slides.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.className = 'slide-dot' + (i === 0 ? ' active' : '');
    dot.setAttribute('aria-label', `Slydis ${i + 1}`);
    dot.addEventListener('click', () => goTo(i));
    dotsContainer.appendChild(dot);
  });

  function updateDots() {
    dotsContainer.querySelectorAll('.slide-dot').forEach((d, i) => {
      d.classList.toggle('active', i === current);
      d.setAttribute('aria-current', i === current ? 'true' : 'false');
    });
  }

  function goTo(index) {
    current = (index + slides.length) % slides.length;
    track.style.transform = `translateX(-${current * 100}%)`;
    updateDots();
    resetTimer();
  }

  function resetTimer() {
    clearInterval(timer);
    timer = setInterval(() => goTo(current + 1), 4500);
  }

  const prevBtn = document.getElementById('slidePrev');
  const nextBtn = document.getElementById('slideNext');
  
  if (prevBtn) prevBtn.addEventListener('click', () => goTo(current - 1));
  if (nextBtn) nextBtn.addEventListener('click', () => goTo(current + 1));

  // Pause on hover
  track.parentElement.addEventListener('mouseenter', () => clearInterval(timer));
  track.parentElement.addEventListener('mouseleave', resetTimer);

  // Touch/swipe support
  let startX = 0;
  track.addEventListener('touchstart', e => { startX = e.touches[0].clientX; });
  track.addEventListener('touchend', e => {
    const diff = startX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) goTo(current + (diff > 0 ? 1 : -1));
  });

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') goTo(current - 1);
    if (e.key === 'ArrowRight') goTo(current + 1);
  });

  resetTimer();
})();

// ===== SMOOTH SCROLL FOR ANCHOR LINKS =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const href = this.getAttribute('href');
    if (href !== '#') {
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  });
});

// ===== ACCESSIBILITY: SKIP TO MAIN CONTENT =====
const skipLink = document.createElement('a');
skipLink.href = '#main';
skipLink.textContent = 'Pereiti prie pagrindinės turinio';
skipLink.className = 'skip-link';
document.body.insertBefore(skipLink, document.body.firstChild);

// ===== PERFORMANCE: LAZY LOAD IMAGES =====
if ('IntersectionObserver' in window) {
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
        }
        imageObserver.unobserve(img);
      }
    });
  });

  document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
}

// ===== LIGHTBOX INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
  const lightbox = GLightbox({
    selector: '.glightbox',
    touchNavigation: true,
    loop: true,
    autoplayVideos: true,
    cssEfects: {
      fade: true,
      zoom: true,
      slide: false
    }
  });
});
