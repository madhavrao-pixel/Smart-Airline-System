/* ═══════════════════════════════════════════════
   APEX VOYAGE — main.js
   Navigation, autocomplete, currency, animations
═══════════════════════════════════════════════ */

const AIRPORTS = [
  { code: 'BOM', city: 'Mumbai',       country: 'India' },
  { code: 'DEL', city: 'Delhi',        country: 'India' },
  { code: 'BLR', city: 'Bangalore',    country: 'India' },
  { code: 'MAA', city: 'Chennai',      country: 'India' },
  { code: 'CCU', city: 'Kolkata',      country: 'India' },
  { code: 'HYD', city: 'Hyderabad',    country: 'India' },
  { code: 'GOI', city: 'Goa',          country: 'India' },
  { code: 'JAI', city: 'Jaipur',       country: 'India' },
  { code: 'DXB', city: 'Dubai',        country: 'UAE' },
  { code: 'SIN', city: 'Singapore',    country: 'Singapore' },
  { code: 'BKK', city: 'Bangkok',      country: 'Thailand' },
  { code: 'KUL', city: 'Kuala Lumpur', country: 'Malaysia' },
  { code: 'NRT', city: 'Tokyo',        country: 'Japan' },
  { code: 'HKG', city: 'Hong Kong',    country: 'HK' },
  { code: 'CMB', city: 'Colombo',      country: 'Sri Lanka' },
  { code: 'KTM', city: 'Kathmandu',    country: 'Nepal' },
];

const RATES = { INR: 1, USD: 83.5, SGD: 62.0, AED: 22.7 };
let currentCurrency = 'INR';

// ── Navbar scroll behaviour ───────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const nav = document.querySelector('.navbar');
  if (nav) {
    const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 40);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  initTabs();
  initPassengersWidget();
  initAutocomplete();
  initTrackFlight();
  initCurrencySwitcher();
  initScrollAnimations();
  initToasts();
  setMinDates();
  initSearchTabs();
});

// ── Trip type tabs ────────────────────────────────────────
function initSearchTabs() {
  document.querySelectorAll('.s-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.s-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    });
  });
}

// ── Passengers widget ─────────────────────────────────────
function initPassengersWidget() {
  const display = document.querySelector('.pax-display');
  const popup   = document.querySelector('.pax-popup');
  if (!display || !popup) return;

  let adults = 1, children = 0, infants = 0;

  display.addEventListener('click', (e) => {
    e.stopPropagation();
    popup.classList.toggle('open');
    display.classList.toggle('open');
  });
  document.addEventListener('click', () => {
    popup.classList.remove('open');
    display.classList.remove('open');
  });

  function updateDisplay() {
    const total = adults + children + infants;
    const txt = total === 1 ? '1 Adult' : `${total} Passengers`;
    display.querySelector('.pax-display-text').textContent = txt;
    document.getElementById('pax-hidden').value = total;
  }

  popup.querySelectorAll('.pax-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const type = btn.dataset.type;
      const dir  = btn.dataset.dir;
      if (type === 'adults') {
        adults = Math.max(1, Math.min(9, adults + (dir === '+' ? 1 : -1)));
      } else if (type === 'children') {
        children = Math.max(0, Math.min(8, children + (dir === '+' ? 1 : -1)));
      } else {
        infants = Math.max(0, Math.min(adults, infants + (dir === '+' ? 1 : -1)));
      }
      popup.querySelector(`[data-count="adults"]`).textContent   = adults;
      popup.querySelector(`[data-count="children"]`).textContent = children;
      popup.querySelector(`[data-count="infants"]`).textContent  = infants;
      updateDisplay();
    });
  });
}

// ── Autocomplete ──────────────────────────────────────────
function initAutocomplete() {
  document.querySelectorAll('[data-autocomplete="airport"]').forEach(input => {
    const dropdown = input.nextElementSibling;
    if (!dropdown || !dropdown.classList.contains('autocomplete-box')) return;

    input.addEventListener('input', () => {
      const q = input.value.toLowerCase();
      const matches = q.length < 1 ? [] :
        AIRPORTS.filter(a =>
          a.code.toLowerCase().startsWith(q) ||
          a.city.toLowerCase().includes(q) ||
          a.country.toLowerCase().includes(q)
        ).slice(0, 6);

      dropdown.innerHTML = '';
      if (matches.length) {
        matches.forEach(a => {
          const item = document.createElement('div');
          item.className = 'ac-item';
          item.innerHTML = `<span class="ac-code">${a.code}</span>
                            <span class="ac-city">${a.city}, ${a.country}</span>`;
          item.addEventListener('mousedown', () => {
            input.value = a.code;
            dropdown.classList.remove('open');
          });
          dropdown.appendChild(item);
        });
        dropdown.classList.add('open');
      } else {
        dropdown.classList.remove('open');
      }
    });

    input.addEventListener('blur', () => {
      setTimeout(() => dropdown.classList.remove('open'), 150);
    });
    input.addEventListener('focus', () => {
      if (input.value.length > 0) input.dispatchEvent(new Event('input'));
    });
  });
}

// ── Track flight ──────────────────────────────────────────
function initTrackFlight() {
  const btn    = document.getElementById('track-btn');
  const input  = document.getElementById('track-input');
  const result = document.getElementById('track-result');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    const fn = (input.value || '').trim().toUpperCase();
    if (!fn) return;
    btn.textContent = '...';
    try {
      const r = await fetch(`/api/track-flight?flight=${fn}`);
      const d = await r.json();
      if (d.found) {
        const cls = 't-' + d.status.toLowerCase().replace(' ', '-');
        result.querySelector('.t-badge').className = `t-badge ${cls}`;
        result.querySelector('.t-badge').textContent = `✈ ${d.flight} — ${d.status}`;
        result.querySelector('.t-progress-fill').style.width = d.progress + '%';
        result.querySelector('.t-label').textContent =
          d.progress === 0 ? 'At gate' :
          d.progress < 30  ? 'Boarding' :
          d.progress < 80  ? 'In flight' : 'Arrived';
        result.classList.add('show');
      } else {
        showToast('Flight not found. Try AV101–AV220.', 'error');
      }
    } catch {
      showToast('Could not fetch flight status.', 'error');
    }
    btn.textContent = 'Track';
  });
}

// ── Currency switcher ─────────────────────────────────────
function initCurrencySwitcher() {
  const sel = document.getElementById('currency-sel');
  if (!sel) return;
  sel.addEventListener('change', () => {
    currentCurrency = sel.value;
    document.querySelectorAll('[data-price-inr]').forEach(el => {
      const inr = parseFloat(el.dataset.priceInr);
      const rate = RATES[currentCurrency] || 1;
      const converted = inr / rate;
      const symbol = currentCurrency === 'INR' ? '₹' : currentCurrency === 'USD' ? '$' : currentCurrency === 'SGD' ? 'S$' : 'AED ';
      el.textContent = symbol + Math.round(converted).toLocaleString();
    });
  });
}

// ── Scroll-triggered animations ───────────────────────────
function initScrollAnimations() {
  const els = document.querySelectorAll('.feat-card, .dest-card, .flight-card');
  if (!els.length) return;

  const obs = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        setTimeout(() => e.target.classList.add('visible'), i * 80);
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  els.forEach(el => obs.observe(el));
}

// ── Toast system ──────────────────────────────────────────
function initToasts() {
  // Render any flash messages as toasts
  document.querySelectorAll('[data-toast]').forEach(el => {
    showToast(el.dataset.toast, el.dataset.toastType || 'info');
  });
}

function showToast(msg, type = 'info') {
  let zone = document.querySelector('.toast-zone');
  if (!zone) {
    zone = document.createElement('div');
    zone.className = 'toast-zone';
    document.body.appendChild(zone);
  }
  const toast = document.createElement('div');
  const icon = type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ';
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `<span>${icon}</span><span>${msg}</span>`;
  zone.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('out');
    toast.addEventListener('animationend', () => toast.remove());
  }, 4000);
}

// ── Set min dates ─────────────────────────────────────────
function setMinDates() {
  const today = new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type="date"]:not([min])').forEach(i => { i.min = today; });
}

// ── Generic tabs ──────────────────────────────────────────
function initTabs() {
  document.querySelectorAll('[data-tabs]').forEach(container => {
    const tabs   = container.querySelectorAll('[data-tab]');
    const panels = container.querySelectorAll('[data-panel]');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        panels.forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        container.querySelector(`[data-panel="${tab.dataset.tab}"]`)?.classList.add('active');
      });
    });
  });
}
