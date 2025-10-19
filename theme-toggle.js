(function () {
  const LINK_ID = 'themeCss';
  const STORAGE_KEY = 'twin_theme_css';
  const DEFAULT_CSS = 'royal.css';

  // ---- Theme helpers ----
  function setTheme(cssFile) {
    const link = document.getElementById(LINK_ID);
    if (!link) return;
    link.href = cssFile;

    // Fade-in the whole app on theme switch
    document.documentElement.style.transition = 'opacity .25s ease';
    document.documentElement.style.opacity = '0';
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        document.documentElement.style.opacity = '1';
        setTimeout(() => {
          document.documentElement.style.transition = '';
        }, 300);
      });
    });

    try { localStorage.setItem(STORAGE_KEY, cssFile); } catch {}
  }

  function getSavedTheme() {
    try { return localStorage.getItem(STORAGE_KEY) || DEFAULT_CSS; }
    catch { return DEFAULT_CSS; }
  }

  function closeMenu(btn, menu) {
    if (!menu) return;
    menu.classList.remove('open');
    if (btn) {
      btn.classList.remove('open'); // rotation is via :hover; keep clean state
      btn.setAttribute('aria-expanded', 'false');
    }
  }

  // ---- Modal helpers ----
  const modalOverlay = () => document.getElementById('modalOverlay');
  const modalEl = () => document.getElementById('modal');
  const modalTitle = () => document.getElementById('modalTitle');
  const modalBody = () => document.getElementById('modalBody');

  function openModal(title, html) {
    const ov = modalOverlay(); const m = modalEl();
    if (!ov || !m) return;

    modalTitle().textContent = title;
    modalBody().innerHTML = html;

    ov.classList.add('open');
    ov.setAttribute('aria-hidden', 'false');

    // animate overlay & modal
    requestAnimationFrame(() => {
      ov.classList.add('fade-in');
      m.classList.add('show');
    });

    // focus trap (simple)
    setTimeout(() => m.focus(), 10);
  }

  function closeModal() {
    const ov = modalOverlay(); const m = modalEl();
    if (!ov || !m) return;

    // animate out
    ov.classList.remove('fade-in');
    m.classList.remove('show');

    const end = () => {
      ov.removeEventListener('transitionend', end);
      ov.classList.remove('open');
      ov.setAttribute('aria-hidden', 'true');
    };
    ov.addEventListener('transitionend', end);
    setTimeout(end, 350);
  }

  // ---- Init menu & actions ----
  function initMenu() {
    const btn = document.getElementById('themeBtn');
    const menu = document.getElementById('themeMenu');
    if (!btn || !menu) return;

    // Toggle open/close
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const opening = !menu.classList.contains('open');
      if (opening) {
        menu.classList.add('open');
        btn.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      } else {
        closeMenu(btn, menu);
      }
    });

    // Click outside to close
    document.addEventListener('click', () => closeMenu(btn, menu));
    // Stop menu clicks from bubbling
    menu.addEventListener('click', (e) => e.stopPropagation());

    // NEW action (clear both panes)
    const newBtn = document.getElementById('menuNew');
    if (newBtn) {
      newBtn.addEventListener('click', () => {
        document.getElementById('messages-basic')?.replaceChildren();
        document.getElementById('messages-plus')?.replaceChildren();
        closeMenu(btn, menu);
      });
    }

    // WHAT IS TWIN?
    const whatBtn = document.getElementById('menuWhatIs');
    if (whatBtn) {
      whatBtn.addEventListener('click', () => {
        const html = `
          <p>The concept behind <strong>TWIN</strong> is a dual-screen assistant that helps you form quick stock expectations or get deeper analysis at the simple touch of a button.</p>
          <p>It's mainly aimed for beginners who are looking to get into investing and understanding stocks.</p>
          <p><strong>TWIN-</strong> gives a simple, intuitive projection using an <em>Exponential Moving Average</em> style drift estimate over your chosen horizon.</p>
          <p><strong>TWIN+</strong> runs diagnostics to inform conviction and risk:</p>
          <ul>
            <li><em>Momentum (12m)</em> price vs. a year ago.</li>
            <li><em>Trend (50/200-DMA slopes)</em> direction/strength of moving averages.</li>
            <li><em>Breakout (Donchian-50)</em> whether price broke the 50-day range high.</li>
            <li><em>Volatility (HAR-RV)</em> forecast of future volatility from realized variance.</li>
            <li><em>Position size suggestion</em> % position to target a chosen annualized volatility.</li>
          </ul>
          <p>These are informational signals, <b> NOT FINANCIAL ADVICE</b>.</p>
        `;
        openModal('What is TWIN?', html);
        closeMenu(btn, menu);
      });
    }

    // HOW TO USE?
    const howBtn = document.getElementById('menuHowTo');
    if (howBtn) {
      howBtn.addEventListener('click', () => {
        const html = `
          <p>Enter a <strong>stock</strong> and a <strong>duration</strong> in the search bar (Tesla in the next 2 weeks).</p>
          <ul>
           <li>Click <strong>TWIN</strong> or on the <strong>'\\'</strong> key to run both TWIN- and TWIN+ together.</li>
            <li>For a simpler experience, click <strong>Analyze with TWIN-</strong> or the <strong>ENTER</strong> key to see just the quick projection.</li>
            <li>For a deeper analysis, click <strong>Analyze with TWIN+</strong> for momentum, trend, breakout, volatility, and position sizing information.</li>
            <li>Use the <strong>theme menu</strong> (bottom-right) to switch themes, read about TWIN, or clear the chat by click on <b>"CLEAR"</b>.</li>
          </ul>
        `;
        openModal('How to use TWIN', html);
        closeMenu(btn, menu);
      });
    }

    // Theme selection
    menu.querySelectorAll('button[data-css]').forEach((b) => {
      b.addEventListener('click', (e) => {
        e.stopPropagation();
        const css = b.getAttribute('data-css');
        if (css) setTheme(css);
        closeMenu(btn, menu);
      });
    });

    // Modal close handlers
    document.getElementById('modalClose')?.addEventListener('click', closeModal);
    modalOverlay()?.addEventListener('click', (e) => {
      // click outside modal box
      if (e.target === modalOverlay()) closeModal();
    });

    // ESC to close modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modalOverlay()?.classList.contains('open')) closeModal();
    });
  }

  // Apply saved theme quickly, then init menu
  document.addEventListener('DOMContentLoaded', () => {
    setTheme(getSavedTheme());
    initMenu();
  });
})();

