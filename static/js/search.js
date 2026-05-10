/* ═══════════════════════════════════════
   APEX VOYAGE — search.js
   Search page: filters, sort, skeleton
═══════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  initSort();
  initFilters();
  initPriceSlider();
  initTimeChips();
  showSkeletonThenResults();
  initScrollAnimations();
});

// ── Skeleton → results ────────────────────────────────────
function showSkeletonThenResults() {
  const skeletons = document.querySelectorAll('.skeleton-card');
  const cards     = document.querySelectorAll('.flight-card');
  if (!skeletons.length) return;

  skeletons.forEach(s => s.classList.add('show'));
  cards.forEach(c => c.style.display = 'none');

  setTimeout(() => {
    skeletons.forEach(s => s.classList.remove('show'));
    cards.forEach(c => {
      c.style.display = '';
      requestAnimationFrame(() => c.classList.add('visible'));
    });
  }, 400);
}

// ── Sort ──────────────────────────────────────────────────
function initSort() {
  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      sortCards(btn.dataset.sort);
    });
  });
}

function sortCards(method) {
  const container = document.getElementById('results-list');
  if (!container) return;
  const cards = [...container.querySelectorAll('.flight-card')];

  cards.sort((a, b) => {
    if (method === 'cheapest') {
      return parseFloat(a.dataset.price || 9e9) - parseFloat(b.dataset.price || 9e9);
    } else if (method === 'fastest') {
      return parseInt(a.dataset.duration || 9999) - parseInt(b.dataset.duration || 9999);
    } else {
      // Best: score = price / duration ratio
      const scoreA = (parseFloat(a.dataset.price) || 0) / (parseInt(a.dataset.duration) || 1);
      const scoreB = (parseFloat(b.dataset.price) || 0) / (parseInt(b.dataset.duration) || 1);
      return scoreA - scoreB;
    }
  });

  cards.forEach(c => {
    c.classList.remove('visible');
    container.appendChild(c);
    requestAnimationFrame(() => c.classList.add('visible'));
  });
}

// ── Filters ───────────────────────────────────────────────
function initFilters() {
  document.querySelectorAll('.filter-option input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', applyFilters);
  });
  document.getElementById('filter-clear-btn')?.addEventListener('click', () => {
    document.querySelectorAll('.filter-option input[type="checkbox"]').forEach(cb => { cb.checked = false; });
    document.querySelectorAll('.time-chip').forEach(c => c.classList.remove('selected'));
    const slider = document.getElementById('price-slider');
    if (slider) { slider.value = slider.max; updatePriceLabel(slider); }
    applyFilters();
  });
}

function applyFilters() {
  const selectedAircraft = [...document.querySelectorAll('[data-filter="aircraft"]:checked')].map(c => c.value);
  const slider = document.getElementById('price-slider');
  const maxPrice = slider ? parseFloat(slider.value) : Infinity;
  const selectedTimeChips = [...document.querySelectorAll('.time-chip.selected')].map(c => c.dataset.slot);

  document.querySelectorAll('.flight-card').forEach(card => {
    let visible = true;
    if (selectedAircraft.length && !selectedAircraft.includes(card.dataset.aircraft)) visible = false;
    if (parseFloat(card.dataset.price) > maxPrice) visible = false;
    if (selectedTimeChips.length) {
      const hour = parseInt(card.dataset.dep?.split(':')[0] || '0');
      const slot = hour < 6 ? 'night' : hour < 12 ? 'morning' : hour < 18 ? 'afternoon' : 'evening';
      if (!selectedTimeChips.includes(slot)) visible = false;
    }
    card.style.display = visible ? '' : 'none';
  });

  const visibleCount = [...document.querySelectorAll('.flight-card')].filter(c => c.style.display !== 'none').length;
  const countEl = document.querySelector('.results-count');
  if (countEl) countEl.textContent = `${visibleCount} flight${visibleCount !== 1 ? 's' : ''} found`;
}

// ── Price slider ──────────────────────────────────────────
function initPriceSlider() {
  const slider = document.getElementById('price-slider');
  if (!slider) return;
  slider.addEventListener('input', () => { updatePriceLabel(slider); applyFilters(); });
  updatePriceLabel(slider);
}

function updatePriceLabel(slider) {
  const el = document.getElementById('price-val');
  if (el) el.textContent = '₹' + parseInt(slider.value).toLocaleString();
}

// ── Time chips ────────────────────────────────────────────
function initTimeChips() {
  document.querySelectorAll('.time-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('selected');
      applyFilters();
    });
  });
}

// ── Price pill selection ──────────────────────────────────
document.addEventListener('click', (e) => {
  const pill = e.target.closest('.price-pill');
  if (!pill) return;
  const card = pill.closest('.flight-card');
  card?.querySelectorAll('.price-pill').forEach(p => p.classList.remove('selected'));
  pill.classList.add('selected');
});

// ── Scroll animations ─────────────────────────────────────
function initScrollAnimations() {
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.08 });
  document.querySelectorAll('.flight-card').forEach(c => obs.observe(c));
}
