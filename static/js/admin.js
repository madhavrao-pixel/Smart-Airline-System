/* ═══════════════════════════════════════════
   APEX VOYAGE — admin.js
   Dashboard charts, tables, modals
═══════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  initTableSearch();
  initAddFlightModal();
  initSidebarNav();
});

// ── Charts (Chart.js) ─────────────────────────────────────
function initCharts() {
  const weeklyEl = document.getElementById('weekly-chart');
  const pieEl    = document.getElementById('pie-chart');
  if (!weeklyEl || !pieEl) return;

  const WEEKLY = window.WEEKLY_DATA || [];
  const ECO    = window.ECO_COUNT   || 0;
  const BIZ    = window.BIZ_COUNT   || 0;
  const FIRST  = window.FIRST_COUNT || 0;

  new Chart(weeklyEl, {
    type: 'bar',
    data: {
      labels: WEEKLY.map(d => d.label),
      datasets: [{
        label: 'Bookings',
        data: WEEKLY.map(d => d.count),
        backgroundColor: 'rgba(201,168,76,0.7)',
        borderColor: '#C9A84C',
        borderWidth: 2,
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { stepSize: 1 } },
        x: { grid: { display: false } }
      }
    }
  });

  new Chart(pieEl, {
    type: 'doughnut',
    data: {
      labels: ['Economy', 'Business', 'First'],
      datasets: [{
        data: [ECO, BIZ, FIRST],
        backgroundColor: ['#C9A84C', '#FF6B35', '#0A1628'],
        borderWidth: 0,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: { position: 'bottom', labels: { padding: 16, font: { size: 12 } } }
      }
    }
  });
}

// ── Table search ──────────────────────────────────────────
function initTableSearch() {
  document.querySelectorAll('.table-search input').forEach(input => {
    input.addEventListener('input', () => {
      const q = input.value.toLowerCase();
      const tbody = input.closest('.admin-section').querySelector('tbody');
      tbody?.querySelectorAll('tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  });
}

// ── Add flight modal ──────────────────────────────────────
function initAddFlightModal() {
  const modal    = document.getElementById('add-flight-modal');
  const openBtn  = document.getElementById('add-flight-btn');
  const closeBtn = document.getElementById('close-flight-modal');
  if (!modal) return;

  openBtn?.addEventListener('click', () => modal.classList.add('open'));
  closeBtn?.addEventListener('click', () => modal.classList.remove('open'));
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.remove('open');
  });
}

// ── Sidebar section navigation ────────────────────────────
function initSidebarNav() {
  document.querySelectorAll('.sidebar-link[data-section]').forEach(link => {
    link.addEventListener('click', () => {
      document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      const target = document.getElementById(link.dataset.section);
      target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}
