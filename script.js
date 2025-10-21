
function scrollDown(messagesEl, smooth = true){
  const scroller = messagesEl?.closest('.chatbox');
  if (!scroller) return;
  try {
    scroller.scrollTo({ top: scroller.scrollHeight, behavior: smooth ? 'smooth' : 'auto' });
  } catch {
    scroller.scrollTop = scroller.scrollHeight;
  }
}

function addLoading(container){
  const l = document.createElement('div');
  l.className = 'loading';
  l.innerHTML = '<span></span><span></span><span></span>';
  container.appendChild(l);
  scrollDown(container, true);
  return l;
}
function fade(el){ el.classList.add('fade'); return el; }

// Inject minimal CSS so you don’t have to edit theme files
(function injectExplainCSS(){
  const css = `
  .explain-actions .xlate{
    color: inherit; background: transparent; border: 1px solid currentColor;
    border-radius: 10px; padding: 8px 12px; font-weight: 700; cursor: pointer;
    transition: transform .18s ease, box-shadow .18s ease, filter .18s ease, opacity .18s ease;
  }
  .explain-actions .xlate:hover{
    transform: translateY(-3px);
    box-shadow: 0 8px 18px rgba(0,0,0,.25);
    filter: brightness(1.05);
  }
  .explain-actions .xlate:active{
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0,0,0,.2);
  }
  @keyframes explain-swap-in{
    from{ opacity:0; transform: translateY(6px) scale(.98); }
    to  { opacity:1; transform: translateY(0)    scale(1);   }
  }
  @keyframes explain-swap-out{
    from{ opacity:1; transform: translateY(0)    scale(1);   }
    to  { opacity:0; transform: translateY(6px) scale(.98); }
  }
  .explain-anim-in{ animation: explain-swap-in .22s ease both; }
  .explain-anim-out{ animation: explain-swap-out .18s ease both; }
  .hidden{ display:none !important; }
  .small{ font-size:12px; }
  .muted{ opacity:.7; }
  `;
  const tag = document.createElement('style');
  tag.setAttribute('data-twin-explain-css','1');
  tag.textContent = css;
  document.head.appendChild(tag);
})();


document.addEventListener('DOMContentLoaded', () => {
  const inputEl = document.getElementById('userInput');
  if (!inputEl) return;

  inputEl.addEventListener('keydown', (e) => {
    if (e.isComposing) return; // ignore IME composition
    const val = (inputEl.value || '').trim();

    // key enter to run the regular twin-
    if (e.key === 'Enter') {
      e.preventDefault();
      if (val) sendBasic();
      return;
    }

    // "\" => analyze both
    // cover layouts: key "\"; code "Backslash"; JP layouts "IntlRo"/"IntlYen"
    const isBackslash =
      e.key === '\\' || e.code === 'Backslash' || e.code === 'IntlRo' || e.code === 'IntlYen';

    if (isBackslash && !e.shiftKey && !e.ctrlKey && !e.altKey && !e.metaKey) {
      e.preventDefault();          // don't insert the "\" into the input
      if (val) sendTwin();         // runs TWIN- and (if duration) TWIN+
      return;
    }
  });
});

// checks the time
const DUR_RE = /(\d+)?\s*(day|days|week|weeks|month|months|year|years)\b/i;
function hasDuration(text){
  const t = (text || '').toLowerCase().trim();
  if (!t) return false;
  if (t.includes('today') || t.includes('tomorrow')) return true;
  if (t.includes('next week') || t.includes('next month') || t.includes('next year')) return true;
  return DUR_RE.test(t);
}

// automatically jump to last event
(function initAutoScroll(){
  ['messages-basic','messages-plus'].forEach(id => {
    const pane = document.getElementById(id);
    if (!pane) return;
    const obs = new MutationObserver(() => scrollDown(pane, true));
    obs.observe(pane, { childList: true, subtree: true, characterData: true });
  });
})();


async function sendBasic() {
  const inputEl = document.getElementById('userInput');
  const q = (inputEl.value || '').trim();
  if (!q) return;

  const pane = document.getElementById('messages-basic');

  const user = document.createElement('div');
  user.className = 'user';
  user.textContent = q.endsWith('?') ? q : `${q}?`;
  fade(user);
  pane.appendChild(user);
  scrollDown(pane, true);

  const loading = addLoading(pane);

  try {
    // FETCH UNCHANGED
    const r = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: q })
    });
    const data = await r.json();
    pane.removeChild(loading);

    const bot = document.createElement('div');
    bot.className = 'bot';

    if (!r.ok || data.error) {
      bot.textContent = data.error || 'Request failed';
      fade(bot); pane.appendChild(bot); scrollDown(pane, true);
      inputEl.value = ''; return;
    }

    // Price-only (no timeframe)
    if (data.mode === 'price_only' || data.result === undefined) {
      bot.innerHTML = `
        <div class="title">${data.stock}</div>
        <div>Current (last close): <strong>$${Number(data.lastClose).toFixed(2)}</strong></div>
        <div class="muted">${data.message || "Add a timeframe (e.g., 'in 3 days') to get a forecast."}</div>
        <div class="sparkline"></div>
        <div class="btnrow">
          <button class="explain-btn" type="button">Explain</button>
          <button class="plus-btn" type="button">TWIN+ it</button>
        </div>
        <div class="explain hidden"></div>
      `;
      fade(bot); pane.appendChild(bot); scrollDown(pane, true);

      attachExplain(bot.querySelector('.explain-btn'), bot.querySelector('.explain'), {
        mode:'price_only', stock:data.stock, lastClose:data.lastClose
      });
      bot.querySelector('.plus-btn').addEventListener('click', () => sendPlus(q));
      renderSparkline(data.stock, bot.querySelector('.sparkline'));
      inputEl.value = '';
      return;
    }

  
    const delta = data.result - data.lastClose;
    const pct   = (delta / data.lastClose) * 100;
    const sign  = delta >= 0 ? '+' : '';
    const back  = data.backtest ? ` | <span class="muted">Backtest MAE (~120d, horizon=${data.duration}): $${data.backtest.mae.toFixed(2)}</span>` : '';

    bot.innerHTML = `
      <div class="title">${data.stock}${data.duration ? ' in ' + data.duration : ''}</div>
      <div>Last close: <strong>$${data.lastClose.toFixed(2)}</strong></div>
      <div>Forecasted price: <strong>$${data.result.toFixed(2)}</strong>
        <span class="${delta>=0 ? 'up' : 'down'}">(${sign}${delta.toFixed(2)} | ${sign}${pct.toFixed(2)}%)</span>
      </div>
      <div class="muted">Method: ${data.method.replace('_',' ')} (drift/day: ${Number(data.drift_per_day).toFixed(4)})${back}</div>
      <div class="sparkline"></div>
      <div class="btnrow">
        <button class="explain-btn" type="button">Explain</button>
        <button class="plus-btn" type="button">TWIN+ it</button>
      </div>
      <div class="explain hidden"></div>
    `;
    fade(bot); pane.appendChild(bot); scrollDown(pane, true);

    attachExplain(bot.querySelector('.explain-btn'), bot.querySelector('.explain'), {
      mode:'forecast', stock:data.stock, duration:data.duration,
      lastClose:data.lastClose, result:data.result,
      delta:delta, pct:pct, method:data.method, driftPerDay:data.drift_per_day,
      backtest:data.backtest || null
    });
    bot.querySelector('.plus-btn').addEventListener('click', () => sendPlus(q));
    renderSparkline(data.stock, bot.querySelector('.sparkline'));

  } catch (e) {
    pane.removeChild(loading);
    const bot = document.createElement('div'); bot.className = 'bot';
    bot.textContent = 'Error: ' + e.message; fade(bot); pane.appendChild(bot); scrollDown(pane, true);
  }

  inputEl.value = '';
}


async function sendPlus(queryFromTwin = null) {
  const inputEl = document.getElementById('userInput');
  const raw = (queryFromTwin ?? inputEl.value);
  const q = (raw || '').trim();
  if (!q) return;

  const pane = document.getElementById('messages-plus');

  if (!hasDuration(q)) {
    const warn = document.createElement('div');
    warn.className = 'bot';
    warn.innerHTML = `
      <div class="title">Need a timeframe</div>
      <div class="muted">TWIN+ needs a horizon. Try: “${q} in 3 days” or “${q} next week”.</div>
    `;
    fade(warn); pane.appendChild(warn); scrollDown(pane, true); return;
  }

  const user = document.createElement('div');
  user.className = 'user';
  user.textContent = q.endsWith('?') ? q : `${q}?`;
  fade(user); pane.appendChild(user); scrollDown(pane, true);

  const loading = addLoading(pane);

  try {
    // FETCH UNCHANGED
    const r = await fetch('http://localhost:5000/predict_plus', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: q })
    });
    const data = await r.json();
    pane.removeChild(loading);

    const bot = document.createElement('div');
    bot.className = 'bot';

    if (!r.ok || data.error) {
      bot.textContent = data.error || 'Request failed';
      fade(bot); pane.appendChild(bot); scrollDown(pane, true); return;
    }

    const d = data.diagnostics || {};
    const voltxt  = d.ann_vol_forecast != null ? `${(d.ann_vol_forecast*100).toFixed(1)}%` : 'n/a';
    const sizetxt = d.position_size != null ? `${(d.position_size*100).toFixed(0)}%` : 'n/a';
    const rangeTxt = (d.donchian50_lo != null && d.donchian50_hi != null)
      ? ` (range ${d.donchian50_lo?.toFixed(2)} – ${d.donchian50_hi?.toFixed(2)})`
      : '';

    
    bot.innerHTML = `
      <div class="title">${data.stock}${data.duration ? ' in ' + data.duration : ''}</div>
      <div class="muted">${data.method.replace('_',' ')}</div>
      <ul>
        <li>12-month momentum: <strong>${(d.momentum_12m*100).toFixed(2)}%</strong></li>
        <li>50/200-DMA slope: <strong>${d.dma50_slope?.toFixed(4)}</strong> / <strong>${d.dma200_slope?.toFixed(4)}</strong></li>
        <li>Donchian (50 days): 
          <strong>${d.donchian50_breakout ? 'BREAKOUT' : 'range'}</strong>${rangeTxt}
          <div class="muted small">
            Above the 50-day high = breakout (strength). Between the 50-day high/low = range (no clear trend). Near/below the low = weakness.
          </div>
        </li>
        <li>Forecast annualized vol (HAR-RV): <strong>${voltxt}</strong></li>
        <li>Position size for ${(d.target_vol*100).toFixed(0)}% vol target: <strong>${sizetxt}</strong></li>
      </ul>
      <div><em>${data.decision}</em></div>
      <div class="btnrow">
        <button class="explain-btn" type="button">Explain</button>
      </div>
      <div class="explain hidden"></div>
    `;
    fade(bot); pane.appendChild(bot); scrollDown(pane, true);

    // pass diagnostics so the Explain can be specific
    const explainPanel = bot.querySelector('.explain');
    attachExplain(bot.querySelector('.explain-btn'), explainPanel, {
      mode: 'plus',
      decision: data.decision,
      diagnostics: d
    });

   

  } catch (e) {
    pane.removeChild(loading);
    const bot = document.createElement('div'); bot.className = 'bot';
    bot.textContent = 'Error: ' + e.message; fade(bot); pane.appendChild(bot); scrollDown(pane, true);
  }
}


async function sendTwin(){
  const q = (document.getElementById('userInput').value || '').trim();
  if (!q) return;
  await sendBasic();
  if (hasDuration(q)) {
    await sendPlus(q);
  } else {
    const pane = document.getElementById('messages-plus');
    const note = document.createElement('div');
    note.className = 'bot';
    note.innerHTML = `
      <div class="title">Need a timeframe</div>
      <div class="muted">To run TWIN+ alongside TWIN-, add a horizon, e.g., “${q} in 3 days”.</div>
    `;
    fade(note); pane.appendChild(note); scrollDown(pane, true);
  }
}

-
function attachExplain(btn, panel, data) {
  const fmt2 = (n) => Number(n).toFixed(2);

  const build = () => {
    // PRICE ONLY
    if (data.mode === 'price_only') {
      return `
        <div class="explain-body">
          <p><strong>What you’re seeing:</strong> Latest closing price for <strong>${data.stock}</strong>.</p>
          <p><strong>Why no forecast?</strong> No timeframe provided. Try “${data.stock} in 3 days”.</p>
        </div>
      `;
    }


    if (data.mode === 'plus') {
      const proHTML = `
       <div class="explain-pro">
    <h4 class="explain-title">What does TWIN+ checks?</h4>
    <ol class="steps">
      <li><strong>Overall direction:</strong> Up or down vs. last year?</li>
      <li><strong>Trend lines:</strong> Are the 50-day and 200-day lines pointing up?</li>
      <li><strong>New high test:</strong> Is today above the past 50-day high (strong) or still inside that range (undecided)?</li>
      <li><strong>Choppiness:</strong> How “jumpy” the stock could be.</li>
      <li><strong>Right-sizing:</strong> A suggested position size so risk stays steady.</li>
    </ol>
    <div class="explain-actions">
      <button class="xlate" type="button" aria-expanded="false" style="color: inherit">Translate</button>
    </div>
    <div class="explain-decision small muted">${data.decision ? 'Summary: ' + data.decision : ''}</div>
  </div>
      `;
      const friendlyHTML = `
        <div class="explain-friendly hidden" aria-hidden="true">
          <h4 class="explain-title">TWIN+ (Simplified)</h4>
          <ul class="bullets">
           <li><strong>Direction:</strong> Are we higher or lower than roughly a year ago?</li>
      <li><strong>Trend:</strong> Are the 50-day and 200-day averages pointing up or down?</li>
      <li><strong>New highs check (50-day):</strong> Is today above the recent 50-day high (strong), in the range (undecided), or near the low (weak)?</li>
      <li><strong>Volatility:</strong> How much the price tends to swing.</li>
      <li><strong>Position size:</strong> A suggested size to keep risk around a steady level.</li>
          </ul>
          <div class="explain-actions">
            <button class="xlate" type="button" aria-expanded="true" style="color: inherit">Back to metrics</button>
          </div>
          <div class="explain-tiny muted">${data.decision ? 'What this means: ' + data.decision : ''}</div>
        </div>
      `;
      return `<div class="explain-body">${proHTML}${friendlyHTML}</div>`;
    }

    
    const dir = (data.delta || 0) >= 0 ? 'up' : 'down';
    const mname = (data.method || '').replace('_',' ');
    const back = data.backtest ? `<li>Recent average error ≈ <strong>$${fmt2(data.backtest.mae)}</strong>.</li>` : '';
    return `
  <div class="explain-body">
        <h4 class="explain-title">What is TWIN- doing?</h4>
        <p><strong>Your request:</strong> “${data.stock}${data.duration ? ' in ' + data.duration : ''}”.</p>
        <p><strong>Result:</strong> We project <strong>$${fmt2(data.result)}</strong> ${dir} from last close by <strong>$${fmt2(data.delta)}</strong> (${fmt2(data.pct || (data.delta/data.lastClose)*100)}%).</p>
        <h4 class="explain-title">How?</h4>
        <ul class="bullets">
          <li><strong>Operation:</strong> Our formula uses an Exponential Moving Average.</li>
          <li><strong>Measure drift:</strong> It then estimates the average daily move from recent market data.</li>
          <li><strong>Projection:</strong> It extends that drift across your chosen period and returns a prediction.</li>
        </ol>
        <ul class="bullets">
          <li><em>Estimated Price Change / Day:</em> ${fmt2(data.driftPerDay)}</li>
          ${back}
        </ul>
        <div class="explain-tiny muted">Quick directional hint | not a guarantee.</div>
      </div>
    `;
  };


  panel.classList.add('hidden');
  panel.style.display = 'none';

  btn.addEventListener('click', () => {
    const willShow = panel.classList.contains('hidden');
    if (willShow) {
      // Fade-in
      panel.innerHTML = build();
      panel.classList.remove('hidden');
      panel.style.display = '';
      panel.classList.remove('fade'); panel.offsetWidth; panel.classList.add('fade');
      btn.textContent = 'Hide';

      
      panel.querySelectorAll('.xlate').forEach(el => {
        el.addEventListener('click', () => {
          const pro = panel.querySelector('.explain-pro');
          const fr  = panel.querySelector('.explain-friendly');
          const showingPro = !pro.classList.contains('hidden');

          const hideEl = showingPro ? pro : fr;
          const showEl = showingPro ? fr  : pro;

          hideEl.classList.remove('explain-anim-in');
          hideEl.classList.add('explain-anim-out');

          hideEl.addEventListener('animationend', function handler(){
            hideEl.classList.add('hidden');
            hideEl.classList.remove('explain-anim-out');

            showEl.classList.remove('hidden');
            showEl.classList.add('explain-anim-in');

            if (showingPro){
              el.textContent = 'Back to metrics';
              el.setAttribute('aria-expanded','true');
            } else {
              el.textContent = 'Translate';
              el.setAttribute('aria-expanded','false');
            }
            hideEl.removeEventListener('animationend', handler);
          }, { once: true });
        });
      });

      const messages = panel.closest('.messages');
      if (messages) scrollDown(messages, true);

    } else {
      // Fade-out
      panel.classList.remove('fade');
      panel.style.transition = 'opacity .25s ease, transform .25s ease';
      panel.style.opacity = '1';
      panel.style.transform = 'translateY(0)';
      requestAnimationFrame(() => {
        panel.style.opacity = '0';
        panel.style.transform = 'translateY(2px)';
      });
      const end = () => {
        panel.removeEventListener('transitionend', end);
        panel.style.transition = ''; panel.style.opacity = ''; panel.style.transform = '';
        panel.classList.add('hidden'); panel.style.display = 'none';
        btn.textContent = 'Explain';
      };
      panel.addEventListener('transitionend', end);
      setTimeout(end, 350);
    }
  });
}


async function renderSparkline(ticker, container) {
  try {
    // FETCH UNCHANGED
    const r = await fetch(`http://localhost:5000/history?ticker=${encodeURIComponent(ticker)}&days=90`);
    const h = await r.json();
    if (!r.ok || h.error || !h.closes || h.closes.length < 2) return;

    const w = 260, hgt = 48, pad = 2;
    const xs = h.closes;
    const min = Math.min(...xs), max = Math.max(...xs);
    const scaleX = (i) => pad + (i * (w - 2*pad)) / (xs.length - 1);
    const scaleY = (v) => pad + (hgt - 2*pad) * (1 - (v - min) / (max - min || 1));
    const points = xs.map((v,i)=> `${scaleX(i)},${scaleY(v)}`).join(' ');
    container.innerHTML = `
      <svg width="${w}" height="${hgt}" viewBox="0 0 ${w} ${hgt}" preserveAspectRatio="none">
        <polyline fill="none" stroke="currentColor" stroke-width="2" points="${points}" />
      </svg>
    `;
    const messages = container.closest('.messages');
    if (messages) scrollDown(messages, true);
  } catch {}
}

