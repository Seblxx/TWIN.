(function () {
  const LINK_ID = 'themeCss';
  const STORAGE_KEY = 'twin_theme_css';
  const DEFAULT_CSS = 'dark.css';

  // Theme list
  const THEMES = [
    { name: 'Royal', file: 'royal.css', color: 'linear-gradient(135deg, #1e3a8a, #3b82f6)' },
    { name: 'Dark', file: 'dark.css', color: '#1a1a2e' },
    { name: 'Light', file: 'light.css', color: '#f0f0f0' },
    { name: 'Monochrome', file: 'monochrome.css', color: '#1e3a5f' },
    { name: 'Liquid Glass', file: 'liquidglass.css', color: '#000000' }
  ];

  let currentThemeIndex = 0;

  // ---- Theme helpers ----
  function setTheme(cssFile) {
    const link = document.getElementById(LINK_ID);
    if (!link) return;

    // Update theme circle color
    updateThemeCircle(cssFile);

    // Fade-in the whole app on theme switch
    document.documentElement.style.transition = 'opacity .25s ease';
    document.documentElement.style.opacity = '0';
    
    // Wait for CSS to load before fading back in
    link.href = cssFile;
    link.onload = () => {
      requestAnimationFrame(() => {
        document.documentElement.style.opacity = '1';
        setTimeout(() => {
          document.documentElement.style.transition = '';
        }, 300);
      });
    };

    try { localStorage.setItem(STORAGE_KEY, cssFile); } catch {}
  }

  function getSavedTheme() {
    try { return localStorage.getItem(STORAGE_KEY) || DEFAULT_CSS; }
    catch { return DEFAULT_CSS; }
  }

  function updateThemeCircle(cssFile) {
    const themeCircle = document.getElementById('themeToggle');
    if (!themeCircle) return;

    const theme = THEMES.find(t => t.file === cssFile);
    if (theme) {
      themeCircle.style.background = theme.color;
      currentThemeIndex = THEMES.indexOf(theme);
    }
  }

  function cycleTheme() {
    currentThemeIndex = (currentThemeIndex + 1) % THEMES.length;
    setTheme(THEMES[currentThemeIndex].file);
  }

  function closeMenu() {
    const menu = document.getElementById('menuOptions');
    const btn = document.getElementById('menuBtn');
    if (menu) menu.classList.remove('open');
    if (btn) {
      btn.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    }
    // Also close the full-page menu overlay if present
    const menuOv = document.getElementById('menuOverlay');
    if (menuOv) menuOv.classList.remove('open');
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

  function showConfirmModal(title, message, onConfirm, closeAfter = true) {
    const html = `
      <p style="margin-bottom:24px;font-size:15px;line-height:1.6;color:var(--text-color,#fff);">${message}</p>
      <div style="display:flex;gap:12px;">
        <button id="confirmYes" style="flex:1;padding:16px;border-radius:12px;border:none;background:var(--primary-gradient,linear-gradient(90deg,#48b6ff,#ff5ea8));color:#000;font-weight:700;cursor:pointer;font-size:16px;transition:all 0.3s ease;box-shadow:0 4px 12px rgba(0,0,0,0.1);">
          Yes
        </button>
        <button id="confirmNo" style="flex:1;padding:16px;border-radius:12px;border:1px solid var(--border-color,rgba(255,255,255,0.3));background:rgba(0,0,0,0.3);color:#fff;font-weight:600;cursor:pointer;font-size:16px;transition:all 0.3s ease;">
          Cancel
        </button>
      </div>
    `;
    openModal(title, html);
    
    document.getElementById('confirmYes')?.addEventListener('click', () => {
      if (onConfirm) onConfirm();
      if (closeAfter) {
        setTimeout(() => closeModal(), 100);
      }
    });
    
    document.getElementById('confirmNo')?.addEventListener('click', closeModal);
  }

  // ---- Init menu & actions ----
  let homeButtonInterval = null;
  
  function initMenu() {
    const btn = document.getElementById('menuBtn');
    const menu = document.getElementById('menuOptions');
    const themeCircle = document.getElementById('themeToggle');
    
    if (!btn || !menu) return;

    // Toggle menu options
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const opening = !menu.classList.contains('open');
      if (opening) {
        menu.classList.add('open');
        btn.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
        // show full-page overlay if present
        const menuOv = document.getElementById('menuOverlay');
        if (menuOv) menuOv.classList.add('open');
      } else {
        closeMenu();
      }
    });

    // Theme circle toggle
    if (themeCircle) {
      themeCircle.addEventListener('click', (e) => {
        e.stopPropagation();
        cycleTheme();
      });
    }

    // Click outside to close menu (without reloading page)
    document.addEventListener('click', (e) => {
      if (menu.classList.contains('open') && !menu.contains(e.target) && !btn.contains(e.target)) {
        closeMenu();
      }
    });

    // Menu overlay click to close (without reloading page)
    const menuOv = document.getElementById('menuOverlay');
    if (menuOv) {
      menuOv.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        closeMenu();
      });
    }

    // HOME/LOGOUT action
    const homeBtn = document.getElementById('menuHome');
    if (homeBtn) {
      // Update button text based on login status
      function updateHomeButtonText() {
        const isLoggedIn = localStorage.getItem('twin_user_logged_in') === 'true';
        homeBtn.textContent = isLoggedIn ? 'LOGOUT' : 'HOME';
      }
      
      updateHomeButtonText();
      
      // Clear previous interval if exists
      if (homeButtonInterval) {
        clearInterval(homeButtonInterval);
      }
      homeButtonInterval = setInterval(updateHomeButtonText, 500);
      
      homeBtn.addEventListener('click', () => {
        const isLoggedIn = localStorage.getItem('twin_user_logged_in') === 'true';
        
        // Save messages before any navigation
        if (typeof window.saveMessages === 'function') {
          window.saveMessages();
        }
        
        if (isLoggedIn) {
          // Show confirmation then logout
          showConfirmModal(
            'Logout',
            'Are you sure you want to logout?',
            () => {
              console.log('[LOGOUT] Logging out...');
              
              // Clear ALL auth data immediately
              localStorage.clear();
              console.log('[LOGOUT] localStorage cleared');
              
              // Sign out from Supabase asynchronously (don't wait)
              if (window.supabaseClient) {
                window.supabaseClient.auth.signOut().catch(() => {});
                console.log('[LOGOUT] Supabase signOut called');
              }
              
              // Clear all intervals to stop background tasks
              const highestId = setTimeout(() => {}, 0);
              for (let i = 0; i < highestId; i++) {
                clearInterval(i);
                clearTimeout(i);
              }
              console.log('[LOGOUT] Cleared all intervals/timeouts');
              
              // Redirect immediately - use anchor element as fallback
              console.log('[LOGOUT] About to navigate to intro.html');
              
              // Create and click anchor element (most reliable method)
              const link = document.createElement('a');
              link.href = '/intro.html';
              link.style.display = 'none';
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            },
            true  // Close modal before redirect
          );
        } else {
          // Not logged in, just go to intro/home
          closeMenu();
          window.location.href = 'intro.html';
        }
      });
    }

    // NEW action (clear both panes)
    const newBtn = document.getElementById('menuNew');
    if (newBtn) {
      newBtn.addEventListener('click', () => {
        showConfirmModal(
          'Clear All Messages?',
          'This will remove all predictions from both TWIN- and TWIN+ panels.',
          () => {
            document.getElementById('messages-basic')?.replaceChildren();
            document.getElementById('messages-plus')?.replaceChildren();
            localStorage.removeItem('twin_messages_basic');
            localStorage.removeItem('twin_messages_plus');
            closeMenu();
          }
        );
      });
    }

    // MY PREDICTIONS (leaderboard)
    const predsBtn = document.getElementById('menuPredictions');
    if (predsBtn) {
      // Update button state based on localStorage (synced from database)
      function updatePredictionsButton() {
        const isLoggedIn = localStorage.getItem('twin_user_logged_in') === 'true';
        
        if (!isLoggedIn) {
          predsBtn.style.display = 'none';
          return;
        }
        
        predsBtn.style.display = '';
        
        // Check localStorage (already synced from database by getSavedPredictions)
        let predictions = [];
        try {
          predictions = JSON.parse(localStorage.getItem('twin_predictions') || '[]');
        } catch (e) {
          predictions = [];
        }
        
        const isEmpty = predictions.length === 0;
        predsBtn.style.opacity = isEmpty ? '0.4' : '1';
        predsBtn.style.cursor = isEmpty ? 'not-allowed' : 'pointer';
        predsBtn.disabled = isEmpty;
      }
      
      // Initial update
      updatePredictionsButton();
      
      // Update when predictions change (events dispatched from getSavedPredictions)
      window.addEventListener('predictionsSaved', updatePredictionsButton);
      window.addEventListener('predictionsCleared', updatePredictionsButton);
      window.addEventListener('predictionDeleted', updatePredictionsButton);
      
      predsBtn.addEventListener('click', () => {
        if (!predsBtn.disabled) {
          // Save messages before navigating (window.location.replace doesn't trigger beforeunload)
          if (typeof window.saveMessages === 'function') {
            window.saveMessages();
          }
          closeMenu();
          window.location.href = 'predictions.html';
        }
      });
    }

    // WHAT IS TWIN?
    const whatBtn = document.getElementById('menuWhatIs');
    if (whatBtn) {
      whatBtn.addEventListener('click', () => {
        const html = `
          <p><strong>TWIN</strong> is a stock forecasting tool that provides quick predictions and detailed analysis.</p>
          <p><strong>TWIN-</strong> delivers fast price predictions using exponential moving averages and drift analysis.</p>
          <p><strong>TWIN+</strong> provides advanced ML-based forecasts with multiple methods (Light ML, Linear Trend, Mean Reversion, GBM) plus diagnostics including momentum, volatility, and position sizing.</p>
          <p><strong>TWIN*</strong> offers heavy ML ensemble models (coming soon).</p>
          <p style="margin-top:16px; font-size:0.9em; opacity:0.7;"><em>Not financial advice. For educational purposes only.</em></p>
        `;
        openModal('What is TWIN?', html);
        closeMenu();
      });
    }

    // HOW TO USE?
    const howBtn = document.getElementById('menuHowTo');
    if (howBtn) {
      howBtn.addEventListener('click', () => {
        const html = `
          <p>Type a stock and a time frame (e.g., <em>"Apple in 5 days"</em>).</p>
          <p>Click <strong>TWIN</strong> for a dual panel prediction or press <strong>ENTER</strong> for a quick prediction.</p>
          <p>You can use our stock and time selector presets if you just want to use it for fun.</p>
          <p>You can clear the tabs by clicking on the <strong>TWIN.</strong> logo or accessing <strong>Clear</strong> from the menu.</p>
          <p>When logged in, you can save predictions and access the predictions interface.</p>
          <p style="margin-top:12px; font-size:0.9em;"><em>Theme: Click bottom-left circle to cycle themes</em></p>
          <p style="margin-top:12px; font-size:0.9em; opacity:0.8;"><strong>Note:</strong> It's preferred to clear your board after returning from predictions to avoid issues, though you can still use and navigate the app.</p>
        `;
        openModal('How to use TWIN', html);
        closeMenu();
      });
    }

    // Theme selection (removed - now using circle toggle)

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
    const savedTheme = getSavedTheme();
    setTheme(savedTheme);
    
    // Find current theme index
    const themeIndex = THEMES.findIndex(t => t.file === savedTheme);
    if (themeIndex !== -1) {
      currentThemeIndex = themeIndex;
    }
    
    initMenu();
    initUserSession();
  });

  // ---- User Session Management ----
  function initUserSession() {
    const isLoggedIn = localStorage.getItem('twin_user_logged_in') === 'true';
    const userEmail = localStorage.getItem('twin_user_email');
    const userBtn = document.getElementById('menuUser');
    const logoutBtn = document.getElementById('menuLogout');
    const emailSpan = document.getElementById('userEmail');

    if (isLoggedIn && userEmail && userBtn && logoutBtn) {
      // Show user info
      userBtn.style.display = 'block';
      logoutBtn.style.display = 'block';
      if (emailSpan) {
        emailSpan.textContent = userEmail;
      }

      // Logout handler
      logoutBtn.addEventListener('click', async () => {
        showConfirmModal(
          'Logout',
          'Are you sure you want to logout?',
          async () => {
            // If using Supabase, sign out properly
            const token = localStorage.getItem('twin_supabase_token');
            if (token) {
              try {
                // Fetch Supabase client config
                const configRes = await fetch('http://127.0.0.1:5000/api/config');
                const config = await configRes.json();
                if (config.supabaseUrl && config.supabaseUrl !== 'YOUR_SUPABASE_URL_HERE') {
                  const supabase = window.supabase.createClient(config.supabaseUrl, config.supabaseKey);
                  await supabase.auth.signOut();
                }
              } catch (e) {
                console.error('Supabase signout error:', e);
              }
            }
            
            // Clear user input field
            const userInput = document.getElementById('userInput');
            if (userInput) {
              userInput.value = '';
            }
            
            // Clear chat messages
            if (window.clearChat) {
              window.clearChat();
            }
            
            // Clear all local storage
            localStorage.clear();
            
            // Redirect immediately
            window.location.replace('intro.html');
          }
        );
      });
    }
  }
  
  // Export functions globally for use in other scripts
  window.closeModal = closeModal;
  window.showConfirmModal = showConfirmModal;
})();

