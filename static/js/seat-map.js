/* ═══════════════════════════════════════════
   APEX VOYAGE — seat-map.js
   Interactive seat selection
═══════════════════════════════════════════ */

let selectedSeat = null;
const BOOKED_SEATS = window.BOOKED_SEATS || [];

document.addEventListener('DOMContentLoaded', () => {
  const classInput = document.getElementById('seat-class-input');
  const initClass  = classInput ? classInput.value : 'Economy';
  renderSeatMap(initClass);

  // Class tab switching
  document.querySelectorAll('.class-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.class-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const cls = tab.dataset.class;
      if (classInput) classInput.value = cls;
      renderSeatMap(cls);
      updateFare(cls);
      updateAIBanner(cls);
      selectedSeat = null;
      document.getElementById('seat-hidden').value = '';
      hideSeatInfo();
    });
  });
});

function renderSeatMap(seatClass) {
  const grid = document.getElementById('seat-grid');
  if (!grid) return;
  grid.innerHTML = '';

  let rows, leftCols, rightCols;
  if (seatClass === 'First') {
    rows = 6; leftCols = ['A']; rightCols = ['B'];
  } else if (seatClass === 'Business') {
    rows = 12; leftCols = ['A','B']; rightCols = ['C','D'];
  } else {
    rows = 30; leftCols = ['A','B','C']; rightCols = ['D','E','F'];
  }

  const allCols = [...leftCols, ...rightCols];

  for (let row = 1; row <= rows; row++) {
    const rowEl = document.createElement('div');
    rowEl.className = 'seat-row';

    // Row number
    const num = document.createElement('span');
    num.className = 'seat-row-num';
    num.textContent = row;
    rowEl.appendChild(num);

    // Left group
    const left = document.createElement('div');
    left.className = 'seat-group';
    leftCols.forEach(col => left.appendChild(makeSeat(row, col, seatClass)));
    rowEl.appendChild(left);

    // Aisle
    const aisle = document.createElement('div');
    aisle.className = 'seat-aisle';
    rowEl.appendChild(aisle);

    // Right group
    const right = document.createElement('div');
    right.className = 'seat-group';
    rightCols.forEach(col => right.appendChild(makeSeat(row, col, seatClass)));
    rowEl.appendChild(right);

    grid.appendChild(rowEl);
  }
}

function makeSeat(row, col, seatClass) {
  const id = `${row}${col}`;
  const el = document.createElement('div');
  el.className = 'seat';
  el.dataset.seat = id;
  el.setAttribute('aria-label', `Seat ${id}`);
  el.setAttribute('role', 'button');
  el.setAttribute('tabindex', '0');
  el.textContent = col;

  // Window seats
  const isWindow = col === 'A' || col === 'F' || (seatClass === 'Business' && (col === 'A' || col === 'D')) || (seatClass === 'First' && col === 'A');
  if (isWindow) el.classList.add('window');

  // Recommended seat
  const recInput = document.getElementById('rec-seat');
  if (recInput && recInput.value === id) el.classList.add('recommended');

  if (BOOKED_SEATS.includes(id)) {
    el.classList.add('occupied');
    el.setAttribute('aria-disabled', 'true');
    el.setAttribute('aria-label', `Seat ${id} (occupied)`);
  } else {
    el.addEventListener('click', () => selectSeat(el, id, seatClass));
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectSeat(el, id, seatClass); }
    });
  }
  return el;
}

function selectSeat(el, seatId, seatClass) {
  // Deselect previous
  document.querySelectorAll('.seat.selected').forEach(s => s.classList.remove('selected'));

  el.classList.add('selected');
  selectedSeat = seatId;
  document.getElementById('seat-hidden').value = seatId;

  // Show seat info
  showSeatInfo(seatId, seatClass);
  showToastIfAvailable(`Seat ${seatId} selected`, 'info');
}

function showSeatInfo(seatId, seatClass) {
  const info = document.querySelector('.seat-selected-info');
  if (!info) return;
  const row = parseInt(seatId);
  const col = seatId.slice(-1);
  const isWindow = col === 'A' || col === 'F' || (seatClass !== 'Economy' && (col === 'A' || col === 'D'));
  const isExtraLeg = (seatClass === 'Economy' && (row === 1 || row === 14 || row === 30));

  let desc = isWindow ? 'Window seat' : 'Aisle/middle seat';
  if (isExtraLeg) desc += ' • Extra legroom';
  if (row <= 5 && seatClass === 'Economy') desc += ' • Front row';

  info.querySelector('.ssi-seat').textContent = seatId;
  info.querySelector('.ssi-desc').textContent  = desc;
  info.classList.add('show');
}

function hideSeatInfo() {
  document.querySelector('.seat-selected-info')?.classList.remove('show');
}

function updateFare(seatClass) {
  const prices   = window.FLIGHT_PRICES || {};
  const price    = prices[seatClass] || 0;
  const gst      = Math.round(price * 0.05);
  const fees     = 450;
  const total    = price + gst + fees;

  const fmt = n => '₹' + n.toLocaleString('en-IN');
  setFareEl('fare-base',  fmt(price));
  setFareEl('fare-gst',   fmt(gst));
  setFareEl('fare-fees',  fmt(fees));
  setFareEl('fare-total', fmt(total));
  setFareEl('fare-class', seatClass);

  const miles = Math.round(price / 10);
  setFareEl('fare-miles', miles.toLocaleString());
}

function updateAIBanner(seatClass) {
  const recs = { Economy: ['14A', 87], Business: ['4A', 89], First: ['2A', 94] };
  const [seat, score] = recs[seatClass] || ['14A', 87];
  const banner = document.getElementById('ai-seat-val');
  const scoreEl = document.getElementById('ai-score-val');
  if (banner)  banner.textContent  = seat;
  if (scoreEl) scoreEl.textContent = score + '%';
  const recInput = document.getElementById('rec-seat');
  if (recInput) recInput.value = seat;
}

function setFareEl(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function showToastIfAvailable(msg, type) {
  if (typeof showToast === 'function') showToast(msg, type);
}
