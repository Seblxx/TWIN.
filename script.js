
// Stock Suggestions and Duration Presets
let selectedStock = '';
let selectedDuration = '';

// Sparkline rendering function (stub for now)
function renderSparkline(ticker, container) {
  // TODO: Implement sparkline visualization
  // For now, just clear the container to prevent errors
  if (container) {
    container.innerHTML = '';
  }
}

function selectStock(name, ticker) {
  selectedStock = ticker;
  document.getElementById('userInput').value = name;
  document.getElementById('stockSuggestions').style.display = 'none';
  document.getElementById('durationPresets').style.display = 'flex';
  document.getElementById('userInput').placeholder = `Now select a duration for ${name}...`;
}

function selectDuration(duration) {
  selectedDuration = duration;
  const input = document.getElementById('userInput');
  input.value = `${input.value} in ${duration}`;
  document.getElementById('durationPresets').style.display = 'none';
  // Auto-submit
  setTimeout(() => sendTwin(), 300);
}

// Show/hide suggestions on input focus
document.addEventListener('DOMContentLoaded', () => {
  // Clear messages on fresh navigation from intro (not from predictions back button)
  const fromPredictions = document.referrer.includes('predictions.html');
  if (!fromPredictions && !localStorage.getItem('twin_user_logged_in')) {
    // Fresh session - clear old messages for blank slate
    localStorage.removeItem('twin_messages_basic');
    localStorage.removeItem('twin_messages_plus');
  }
  
  const userInput = document.getElementById('userInput');
  const suggestions = document.getElementById('stockSuggestions');
  const presets = document.getElementById('durationPresets');
  
  userInput.addEventListener('focus', () => {
    if (!userInput.value) {
      suggestions.style.display = 'block';
      presets.style.display = 'none';
    }
  });
  
  userInput.addEventListener('input', () => {
    if (!userInput.value) {
      suggestions.style.display = 'block';
      presets.style.display = 'none';
    } else {
      suggestions.style.display = 'none';
    }
  });
  
  // Close on click outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.input-group')) {
      suggestions.style.display = 'none';
      presets.style.display = 'none';
    }
  });
});

function scrollDown(messagesEl, smooth = true){
  const scroller = messagesEl?.closest('.chatbox');
  if (!scroller) return;
  try {
    scroller.scrollTo({ top: scroller.scrollHeight, behavior: smooth ? 'smooth' : 'auto' });
  } catch {
    scroller.scrollTop = scroller.scrollHeight;
  }
}

// ==================== PREDICTIONS STORAGE ====================
// Save and restore chat messages
function saveMessages() {
  try {
    const basicMessages = document.getElementById('messages-basic')?.innerHTML || '';
    const plusMessages = document.getElementById('messages-plus')?.innerHTML || '';
    localStorage.setItem('twin_messages_basic', basicMessages);
    localStorage.setItem('twin_messages_plus', plusMessages);
  } catch (e) {
    console.error('Failed to save messages:', e);
  }
}

function restoreMessages() {
  try {
    const basicMessages = localStorage.getItem('twin_messages_basic');
    const plusMessages = localStorage.getItem('twin_messages_plus');
    const isLoggedIn = localStorage.getItem('twin_user_logged_in') === 'true';
    
    if (basicMessages) {
      let html = basicMessages;
      // Remove star buttons if not logged in
      if (!isLoggedIn) {
        html = html.replace(/<button[^>]*class="[^"]*star-save-btn[^"]*"[^>]*>[\s\S]*?<\/button>/g, '');
      }
      document.getElementById('messages-basic').innerHTML = html;
    }
    if (plusMessages) {
      document.getElementById('messages-plus').innerHTML = plusMessages;
    }
  } catch (e) {
    console.error('Failed to restore messages:', e);
  }
}

function savePrediction(pred) {
  try {
    const userEmail = localStorage.getItem('twin_user_email') || 'guest';
    const token = localStorage.getItem('twin_supabase_token');
    
    // Add user email to prediction data
    pred.userEmail = userEmail;
    
    // If guest or no token, fall back to localStorage
    if (userEmail === 'guest' || !token) {
      const saved = JSON.parse(localStorage.getItem('twin_predictions') || '[]');
      saved.push(pred);
      localStorage.setItem('twin_predictions', JSON.stringify(saved));
      console.log('Prediction saved to localStorage (guest):', pred);
      return;
    }
    
    // Save to backend for authenticated users with token
    fetch('/api/predictions/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(pred)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log('Prediction saved to database:', pred);
      } else {
        console.error('Failed to save prediction:', data.error);
        // Fallback to localStorage
        const saved = JSON.parse(localStorage.getItem('twin_predictions') || '[]');
        saved.push(pred);
        localStorage.setItem('twin_predictions', JSON.stringify(saved));
      }
    })
    .catch(error => {
      console.error('Error saving prediction:', error);
      // Fallback to localStorage
      const saved = JSON.parse(localStorage.getItem('twin_predictions') || '[]');
      saved.push(pred);
      localStorage.setItem('twin_predictions', JSON.stringify(saved));
    });
  } catch (e) {
    console.error('Failed to save prediction:', e);
  }
}

function getSavedPredictions() {
  try {
    const isLoggedIn = localStorage.getItem('twin_user_logged_in') === 'true';
    const userEmail = localStorage.getItem('twin_user_email') || 'guest';
    const token = localStorage.getItem('twin_supabase_token');
    
    // If guest or no token or not logged in, use localStorage
    if (!isLoggedIn || userEmail === 'guest' || !token) {
      return Promise.resolve(JSON.parse(localStorage.getItem('twin_predictions') || '[]'));
    }
    
    // Fetch from backend for authenticated users with token
    return fetch('/api/predictions/user', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Convert database format to frontend format
          return data.predictions.map(p => ({
            id: p.id,
            stock: p.stock,
            duration: p.duration,
            lastClose: p.last_close,
            predictedPrice: p.predicted_price,
            method: p.method,
            delta: p.delta,
            pct: p.pct,
            timestamp: p.timestamp,
            feedback: p.feedback
          }));
        }
        return [];
      })
      .catch(error => {
        // Suppress fetch errors during logout/navigation transitions
        if (error.message !== 'Failed to fetch' && error.name !== 'TypeError') {
          console.error('Error fetching predictions:', error);
        }
        // Fallback to localStorage
        return JSON.parse(localStorage.getItem('twin_predictions') || '[]');
      });
  } catch {
    return Promise.resolve([]);
  }
}

function clearPredictions() {
  try {
    localStorage.removeItem('twin_predictions');
  } catch (e) {
    console.error('Failed to clear predictions:', e);
  }
}

function showLeaderboard() {
  // Check if user is logged in
  const isLoggedIn = localStorage.getItem('twin_user_logged_in') === 'true';
  if (!isLoggedIn) {
    // Silently do nothing - button should be hidden anyway
    return;
  }

  // Get predictions asynchronously
  getSavedPredictions().then(predictions => {
    if (predictions.length === 0) {
      // Silently do nothing - button should be disabled anyway
      return;
    }

    let html = '<div class="leaderboard-container">';
    html += '<h3 style="margin-bottom:16px;">🏆 PREDICTIONS Leaderboard</h3>';
    html += '<p class="muted small" style="margin-bottom:16px;">Check if your predictions were accurate. Your feedback strengthens our model!</p>';
    html += '<div class="predictions-list">';
    
    predictions.reverse().forEach((pred, idx) => {
      const date = new Date(pred.timestamp);
      const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
      const arrow = pred.delta >= 0 ? '📈' : '📉';
      const deltaClass = pred.delta >= 0 ? 'up' : 'down';
      const hasFeedback = pred.feedback !== undefined;
      const feedbackClass = pred.feedback === 'yes' ? 'feedback-yes' : pred.feedback === 'no' ? 'feedback-no' : '';
    
    html += `
      <div class="prediction-card ${feedbackClass}" data-pred-id="${pred.id}">
        <div class="pred-header">
          <strong>${arrow} ${pred.stock}</strong>
          <span class="pred-date small muted">${dateStr}</span>
        </div>
        <div class="pred-body">
          <div class="pred-row">
            <span>Last Close:</span>
            <strong>$${pred.lastClose.toFixed(2)}</strong>
          </div>
          <div class="pred-row">
            <span>Predicted (${pred.duration}):</span>
            <strong class="${deltaClass}">$${pred.predictedPrice.toFixed(2)}</strong>
          </div>
          <div class="pred-row">
            <span>Expected Change:</span>
            <strong class="${deltaClass}">${pred.delta >= 0 ? '+' : ''}${pred.delta.toFixed(2)} (${pred.pct >= 0 ? '+' : ''}${pred.pct.toFixed(2)}%)</strong>
          </div>
          <div class="pred-row small muted">
            <span>Method:</span>
            <span>${pred.method.replace('_', ' ')}</span>
          </div>
          ${!hasFeedback ? `
          <div class="pred-feedback">
            <span class="feedback-label">Was this accurate?</span>
            <div class="feedback-buttons">
              <button class="feedback-btn feedback-yes-btn" onclick="submitFeedback('${pred.id}', 'yes')">✓ Yes</button>
              <button class="feedback-btn feedback-no-btn" onclick="submitFeedback('${pred.id}', 'no')">✗ No</button>
            </div>
          </div>
          ` : `
          <div class="pred-feedback-complete">
            <span class="feedback-result ${pred.feedback === 'yes' ? 'feedback-yes-text' : 'feedback-no-text'}">
              ${pred.feedback === 'yes' ? '✓ Marked accurate' : '✗ Marked inaccurate'}
            </span>
            ${pred.feedback === 'no' && pred.inaccuracyValue ? `
              <div class="inaccuracy-details" style="margin-top:8px;font-size:12px;opacity:0.8;">
                Off by ${pred.inaccuracyType === 'percentage' ? pred.inaccuracyValue.toFixed(2) + '%' : '$' + pred.inaccuracyValue.toFixed(2)}
                ${pred.inaccuracyNotes ? '<br><em>"' + pred.inaccuracyNotes + '"</em>' : ''}
              </div>
            ` : ''}
          </div>
          `}
        </div>
      </div>
    `;
  });
  
  html += '</div>';
  html += '<button class="clear-predictions-btn" id="clearPredictionsBtn">Clear All Predictions</button>';
  html += '</div>';
  
  // Use the modal system
  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');
  const modalOverlay = document.getElementById('modalOverlay');
  const modal = document.getElementById('modal');
  
  if (modalTitle && modalBody && modalOverlay && modal) {
    modalTitle.textContent = 'PREDICTIONS';
    modalBody.innerHTML = html;
    modalOverlay.classList.add('open', 'fade-in');
    modalOverlay.setAttribute('aria-hidden', 'false');
    requestAnimationFrame(() => {
      modal.classList.add('show');
    });
    
    // Add event listener for clear button
    const clearBtn = document.getElementById('clearPredictionsBtn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        showNotification('Clear All Predictions?', 'This action cannot be undone. Continue?');
        
        // Override OK button to handle clear
        const okBtn = document.getElementById('notificationOk');
        const notifOverlay = document.getElementById('notificationOverlay');
        const newOkBtn = okBtn.cloneNode(true);
        okBtn.parentNode.replaceChild(newOkBtn, okBtn);
        
        newOkBtn.addEventListener('click', () => {
          notifOverlay.classList.remove('show');
          clearPredictions();
          location.reload();
        });
      });
    }
  }
  });  // Close the getSavedPredictions().then() callback
}

// Submit feedback for a prediction
function submitFeedback(predId, feedback) {
  try {
    const predictions = JSON.parse(localStorage.getItem('twin_predictions') || '[]');
    const predIndex = predictions.findIndex(p => p.id === predId);
    
    if (predIndex === -1) {
      console.error('Prediction not found:', predId);
      return;
    }
    
    // If feedback is "no", show inaccuracy modal first
    if (feedback === 'no') {
      showInaccuracyModal(predId, predictions[predIndex]);
      return;
    }
    
    // For "yes" feedback, proceed normally
    completeFeedbackSubmission(predId, feedback, null, null);
    
  } catch (e) {
    console.error('Failed to submit feedback:', e);
    showNotification('Error', 'Failed to save feedback. Please try again.');
  }
}

// Show modal to capture inaccuracy details when user clicks "No"
function showInaccuracyModal(predId, prediction) {
  const modalOverlay = document.getElementById('modalOverlay');
  const modal = document.getElementById('modal');
  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');
  
  const currentPrice = prediction.predictedPrice; // You could fetch actual current price here
  const predictedPrice = prediction.predictedPrice;
  const lastClose = prediction.lastClose;
  
  const html = `
    <div class="inaccuracy-form">
      <p style="margin-bottom:20px;font-size:15px;opacity:0.9;">Help us improve! How inaccurate was this prediction?</p>
      
      <div class="prediction-summary" style="background:rgba(255,255,255,0.05);padding:14px;border-radius:10px;margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
          <span style="opacity:0.8;">Stock:</span>
          <strong>${prediction.stock}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
          <span style="opacity:0.8;">Predicted:</span>
          <strong>$${predictedPrice.toFixed(2)}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;">
          <span style="opacity:0.8;">Last Close:</span>
          <strong>$${lastClose.toFixed(2)}</strong>
        </div>
      </div>
      
      <div class="form-group" style="margin-bottom:16px;">
        <label style="display:block;margin-bottom:8px;font-weight:600;font-size:14px;">Inaccuracy Type:</label>
        <div style="display:flex;gap:10px;">
          <button class="inaccuracy-type-btn active" data-type="percentage" style="flex:1;padding:10px;border-radius:8px;border:2px solid rgba(59,130,246,0.6);background:rgba(59,130,246,0.15);color:#3b82f6;font-weight:600;cursor:pointer;transition:all 0.2s ease;">
            Percentage
          </button>
          <button class="inaccuracy-type-btn" data-type="money" style="flex:1;padding:10px;border-radius:8px;border:2px solid rgba(255,255,255,0.2);background:transparent;color:#fff;font-weight:600;cursor:pointer;transition:all 0.2s ease;">
            Money Value
          </button>
        </div>
      </div>
      
      <div class="form-group" style="margin-bottom:20px;">
        <label for="inaccuracyValue" style="display:block;margin-bottom:8px;font-weight:600;font-size:14px;">
          <span id="inaccuracyLabel">Percentage Off (%)</span>
        </label>
        <input type="number" id="inaccuracyValue" placeholder="e.g., 5" step="0.01" 
          style="width:100%;padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);color:#fff;font-size:15px;outline:none;transition:all 0.2s ease;">
      </div>
      
      <div class="form-group" style="margin-bottom:20px;">
        <label for="inaccuracyNotes" style="display:block;margin-bottom:8px;font-weight:600;font-size:14px;">Additional Notes (Optional)</label>
        <textarea id="inaccuracyNotes" placeholder="Any other feedback..." rows="3"
          style="width:100%;padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);color:#fff;font-size:14px;outline:none;resize:vertical;font-family:inherit;"></textarea>
      </div>
      
      <div style="display:flex;gap:10px;">
        <button id="submitInaccuracy" style="flex:1;padding:12px;border-radius:10px;border:none;background:#ef4444;color:#fff;font-weight:700;cursor:pointer;font-size:15px;transition:all 0.2s ease;">
          Submit Feedback
        </button>
        <button id="cancelInaccuracy" style="padding:12px 20px;border-radius:10px;border:1px solid rgba(255,255,255,0.3);background:transparent;color:#fff;font-weight:600;cursor:pointer;transition:all 0.2s ease;">
          Cancel
        </button>
      </div>
    </div>
  `;
  
  modalTitle.textContent = 'Prediction Inaccuracy Details';
  modalBody.innerHTML = html;
  
  // Show modal with smooth animation
  modalOverlay.classList.add('open', 'fade-in');
  modalOverlay.setAttribute('aria-hidden', 'false');
  requestAnimationFrame(() => {
    modal.classList.add('show');
  });
  
  // Type toggle functionality
  const typeButtons = modalBody.querySelectorAll('.inaccuracy-type-btn');
  const inaccuracyLabel = modalBody.querySelector('#inaccuracyLabel');
  const inaccuracyInput = modalBody.querySelector('#inaccuracyValue');
  let selectedType = 'percentage';
  
  typeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      typeButtons.forEach(b => {
        b.classList.remove('active');
        b.style.borderColor = 'rgba(255,255,255,0.2)';
        b.style.background = 'transparent';
        b.style.color = '#fff';
      });
      btn.classList.add('active');
      btn.style.borderColor = 'rgba(59,130,246,0.6)';
      btn.style.background = 'rgba(59,130,246,0.15)';
      btn.style.color = '#3b82f6';
      
      selectedType = btn.getAttribute('data-type');
      if (selectedType === 'percentage') {
        inaccuracyLabel.textContent = 'Percentage Off (%)';
        inaccuracyInput.placeholder = 'e.g., 5';
      } else {
        inaccuracyLabel.textContent = 'Money Value Off ($)';
        inaccuracyInput.placeholder = 'e.g., 12.50';
      }
    });
  });
  
  // Submit button
  modalBody.querySelector('#submitInaccuracy').addEventListener('click', () => {
    const value = parseFloat(inaccuracyInput.value);
    const notes = modalBody.querySelector('#inaccuracyNotes').value.trim();
    
    if (!value || value <= 0) {
      inaccuracyInput.style.borderColor = '#ef4444';
      setTimeout(() => {
        inaccuracyInput.style.borderColor = 'rgba(255,255,255,0.2)';
      }, 2000);
      return;
    }
    
    const inaccuracyData = {
      type: selectedType,
      value: value,
      notes: notes
    };
    
    completeFeedbackSubmission(predId, 'no', inaccuracyData, notes);
    // Close modal using the global closeModal from theme-toggle.js
    if (window.closeModal) {
      window.closeModal();
    }
  });
  
  // Cancel button
  modalBody.querySelector('#cancelInaccuracy').addEventListener('click', () => {
    if (window.closeModal) {
      window.closeModal();
    }
  });
}

// Complete feedback submission (called after inaccuracy modal for "no" or directly for "yes")
function completeFeedbackSubmission(predId, feedback, inaccuracyData, notes) {
  try {
    const predictions = JSON.parse(localStorage.getItem('twin_predictions') || '[]');
    const predIndex = predictions.findIndex(p => p.id === predId);
    
    if (predIndex === -1) {
      console.error('Prediction not found:', predId);
      return;
    }
    
    // Update prediction with feedback
    predictions[predIndex].feedback = feedback;
    predictions[predIndex].feedbackTimestamp = new Date().toISOString();
    
    if (inaccuracyData) {
      predictions[predIndex].inaccuracyType = inaccuracyData.type;
      predictions[predIndex].inaccuracyValue = inaccuracyData.value;
      predictions[predIndex].inaccuracyNotes = inaccuracyData.notes || '';
    }
    
    localStorage.setItem('twin_predictions', JSON.stringify(predictions));
    
    // Save feedback to backend
    fetch('http://localhost:5000/save_feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        predictionId: predId,
        feedback: feedback,
        stock: predictions[predIndex].stock,
        duration: predictions[predIndex].duration,
        predictedPrice: predictions[predIndex].predictedPrice,
        lastClose: predictions[predIndex].lastClose,
        method: predictions[predIndex].method,
        timestamp: predictions[predIndex].timestamp,
        feedbackTimestamp: predictions[predIndex].feedbackTimestamp,
        userEmail: localStorage.getItem('twin_user_email') || 'guest',
        inaccuracyData: inaccuracyData || null
      })
    }).catch(err => console.error('Failed to save feedback to backend:', err));
    
    // Show thank you message
    const thankYouMsg = document.createElement('div');
    thankYouMsg.className = 'feedback-thank-you';
    thankYouMsg.innerHTML = '<p>✨ Thank you for strengthening our model! ✨</p>';
    thankYouMsg.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(59,130,246,.95);color:#fff;padding:20px 40px;border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,.4);z-index:10001;font-weight:700;font-size:18px;text-align:center;animation:fadeInScale .3s ease;';
    document.body.appendChild(thankYouMsg);
    
    setTimeout(() => {
      thankYouMsg.style.animation = 'fadeOutScale .3s ease';
      setTimeout(() => {
        document.body.removeChild(thankYouMsg);
        // Refresh leaderboard
        showLeaderboard();
      }, 300);
    }, 2000);
    
  } catch (e) {
    console.error('Failed to submit feedback:', e);
    showNotification('Error', 'Failed to save feedback. Please try again.');
  }
}

// Make functions globally accessible
// Save messages periodically and before page unload
window.addEventListener('beforeunload', saveMessages);

// Restore messages when page loads
window.addEventListener('DOMContentLoaded', () => {
  restoreMessages();
});

// Save messages every 5 seconds
setInterval(saveMessages, 5000);

window.saveMessages = saveMessages;
window.restoreMessages = restoreMessages;
window.savePrediction = savePrediction;
window.showLeaderboard = showLeaderboard;
window.clearPredictions = clearPredictions;
window.submitFeedback = submitFeedback;


function getCompanyDomain(ticker) {
  // Map common tickers to their domains for logo fetching
  const domainMap = {
    'AAPL': 'apple.com', 'MSFT': 'microsoft.com', 'GOOGL': 'google.com', 'GOOG': 'google.com',
    'AMZN': 'amazon.com', 'TSLA': 'tesla.com', 'NVDA': 'nvidia.com', 'META': 'meta.com',
    'NFLX': 'netflix.com', 'AMD': 'amd.com', 'INTC': 'intel.com', 'DIS': 'disney.com',
    'PYPL': 'paypal.com', 'ADBE': 'adobe.com', 'CSCO': 'cisco.com', 'ORCL': 'oracle.com',
    'CRM': 'salesforce.com', 'IBM': 'ibm.com', 'UBER': 'uber.com', 'LYFT': 'lyft.com',
    'SNAP': 'snap.com', 'SQ': 'block.xyz', 'SHOP': 'shopify.com', 'SPOT': 'spotify.com',
    'ZM': 'zoom.us', 'DOCU': 'docusign.com', 'COIN': 'coinbase.com', 'PLTR': 'palantir.com',
    'SNOW': 'snowflake.com', 'BABA': 'alibaba.com', 'HOOD': 'robinhood.com'
  };
  return domainMap[ticker] || `${ticker.toLowerCase()}.com`;
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
  .explain-actions .copy-btn{
    color: inherit; background: transparent; border: 1px solid currentColor;
    border-radius: 10px; padding: 8px 12px; font-weight: 700; cursor: pointer;
    transition: transform .18s ease, box-shadow .18s ease, filter .18s ease, background .18s ease, border-color .18s ease;
    display: inline-flex; align-items: center; gap: 6px;
  }
  .explain-actions .copy-btn:hover{
    transform: translateY(-3px);
    box-shadow: 0 8px 18px rgba(0,0,0,.25);
    filter: brightness(1.05);
  }
  .explain-actions .copy-btn:active{
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
  
  /* Mobile & Responsive Scrolling */
  @media screen and (max-width: 768px) {
    body {
      overflow-x: hidden;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
      touch-action: manipulation;
      position: relative;
    }
    
    .shell {
      min-height: 100vh !important;
      overflow-x: hidden !important;
    }
    
    .container, .main-container {
      width: 100% !important;
      max-width: 100vw !important;
      padding: 8px !important;
      margin: 0 !important;
      overflow-x: hidden;
    }
    
    .grid {
      display: flex !important;
      flex-direction: column !important;
      gap: 12px !important;
      padding: 0 8px !important;
    }
    
    .card {
      width: 100% !important;
      min-height: 300px !important;
      max-height: 400px !important;
    }
    
    .chatbox {
      height: 300px !important;
      max-height: 400px !important;
      overflow-y: auto !important;
      overflow-x: hidden !important;
      -webkit-overflow-scrolling: touch !important;
      scroll-behavior: smooth !important;
      padding: 8px !important;
    }
    
    .bot, .user {
      max-width: calc(100% - 20px) !important;
      word-wrap: break-word !important;
      overflow-wrap: break-word !important;
      margin: 8px 0 !important;
    }
    
    .flip-card {
      max-width: 100% !important;
      overflow: hidden !important;
    }
    
    .btnrow {
      flex-wrap: wrap !important;
      gap: 8px !important;
    }
    
    .action-btn {
      min-width: 80px !important;
      font-size: 12px !important;
      padding: 6px 12px !important;
    }
    
    .method-menu {
      max-width: 100% !important;
      overflow-x: auto !important;
      -webkit-overflow-scrolling: touch !important;
    }
    
    .suggestions {
      max-width: 100% !important;
      overflow-x: auto !important;
      -webkit-overflow-scrolling: touch !important;
      flex-wrap: wrap !important;
    }
    
    .suggestion-chip {
      min-width: 90px !important;
      font-size: 11px !important;
    }
    
    /* Ensure input area is accessible and sticky */
    .topbar {
      position: sticky !important;
      top: 0 !important;
      z-index: 100 !important;
      backdrop-filter: blur(10px) !important;
      border-bottom: 1px solid rgba(255,255,255,0.1) !important;
      padding: 12px 16px !important;
      display: flex !important;
      justify-content: space-between !important;
      align-items: center !important;
      flex-wrap: nowrap !important;
      gap: 16px !important;
    }
    
    .controls {
      display: flex !important;
      align-items: center !important;
      gap: 12px !important;
      flex: 1 !important;
      max-width: calc(100% - 140px) !important;
    }
    
    .input-group {
      display: flex !important;
      flex: 1 !important;
      max-width: 100% !important;
      min-width: 0 !important;
    }
    
    /* Hide placeholder text on mobile to save space */
    .input-group input::placeholder {
      color: transparent !important;
    }
    
    .input-group input {
      font-size: 16px !important; /* Prevents zoom on iOS */
      flex: 1 !important;
      min-width: 0 !important;
    }
    
    .btn-both-inside {
      white-space: nowrap !important;
      flex-shrink: 0 !important;
    }
    
    .btn-plus {
      white-space: nowrap !important;
      flex-shrink: 0 !important;
    }
    
    .brand {
      flex-shrink: 0 !important;
      min-width: 120px !important;
    }
    
    .app-title {
      font-size: 26px !important;
      font-weight: 900 !important;
      letter-spacing: -0.5px !important;
    }
    
    /* Hide placeholder text on mobile to save space */
    .input-group input::placeholder {
      color: transparent !important;
    }
    
    .input-group input {
      font-size: 16px !important; /* Prevents zoom on iOS */
      flex: 1 !important;
      min-width: 0 !important;
    }
    
    /* Theme button adjustments for mobile */
    .theme-fab {
      right: 16px !important;
      bottom: 16px !important;
    }
    
    .theme-btn {
      width: 44px !important;
      height: 44px !important;
    }
    
    .theme-menu {
      right: 0 !important;
      bottom: 56px !important;
      min-width: 240px !important;
      max-width: calc(100vw - 32px) !important;
    }
  }
  
  /* Tablet adjustments */
  @media screen and (max-width: 1024px) and (min-width: 769px) {
    .grid {
      gap: 16px !important;
      padding: 0 16px !important;
    }
    
    .chatbox {
      max-height: 500px !important;
    }
  }
  
  /* General scrolling improvements for all screen sizes */
  html {
    scroll-behavior: smooth;
    overflow-x: hidden;
  }
  
  body {
    overflow-x: hidden;
    position: relative;
  }
  
  .chatbox {
    scroll-behavior: smooth;
    scrollbar-width: thin;
    scrollbar-color: rgba(255,255,255,0.3) transparent;
  }
  
  .chatbox::-webkit-scrollbar {
    width: 6px;
  }
  
  .chatbox::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .chatbox::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.3);
    border-radius: 3px;
  }
  
  .chatbox::-webkit-scrollbar-thumb:hover {
    background: rgba(255,255,255,0.5);
  }
  /* --- Equation / Method toggle UI --- */
  .method-row{ margin-top:6px; font-size:13px; display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
  .method-row .methods{ display:inline-flex; gap:4px; }
  .method-btn{ 
    cursor:pointer; 
    background:rgba(255,255,255,0.08); 
    color:inherit; 
    border:2px solid currentColor; 
    padding:6px 12px; 
    border-radius:20px; 
    font-size:12px; 
    font-weight:500;
    transition:all .18s ease;
    opacity:1;
  }
  .method-btn:hover{ 
    background:var(--accent,#3b6df0); 
    color:#fff; 
    border-color:var(--accent,#3b6df0);
    transform:translateY(-3px); 
    box-shadow:0 6px 16px rgba(59,109,240,.4);
  }
  .method-btn.active{ 
    background:var(--accent, #3b6df0); 
    color:#fff; 
    border-color:var(--accent, #3b6df0);
    transform:translateY(-2px); 
    box-shadow:0 4px 12px rgba(59,109,240,.3);
  }

  .method-toggle{
    cursor:pointer; 
    background:rgba(255,255,255,0.08); 
    color:inherit; 
    border:2px solid currentColor; 
    padding:8px 16px; 
    border-radius:20px; 
    font-size:12px; 
    font-weight:500;
    transition:all .18s ease;
    display:inline-block;
    margin-bottom:8px;
  }
  .method-toggle:hover{ 
    background:var(--accent,#3b6df0); 
    color:#fff; 
    border-color:var(--accent,#3b6df0);
    transform:translateY(-2px); 
    box-shadow:0 4px 12px rgba(59,109,240,.4);
  }
  /* subtle tap animation for the equations/method toggle */
  @keyframes method-tap{
    0%   { filter:none; }
    50%  { filter:brightness(1.08); }
    100% { filter:none; }
  }
  .method-toggle.tap{
    animation: method-tap 220ms ease 1;
  }
  
  .method-menu{
    display:flex;
    flex-wrap:wrap;
    gap:6px;
    animation:fadeInUp .35s ease-out;
  }
  .method-menu.hidden{
    display:none;
  }
  .backtest-row{ margin-top:4px; font-size:12px; }
  .drift-chip{ display:inline-block; padding:2px 6px; border-radius:12px; background:var(--bg-alt,#222); font-size:11px; opacity:.8; }
  @media (max-width:640px){ .method-row{ font-size:12px; } }
  /* TWIN+ collapsible diagnostics */
  .plus-summary{ font-size:13px; margin-bottom:4px; }
  .metrics-list{ margin:0; padding-left:18px; }
  /* Suggestions (Did you mean...) */
  .suggestions{ margin-top:8px; display:flex; flex-wrap:wrap; gap:6px; }
  .suggestion-btn{ cursor:pointer; background:var(--bg-alt,#222); color:inherit; border:1px solid currentColor; padding:4px 10px; border-radius:16px; font-size:12px; line-height:1.2; display:flex; flex-direction:column; align-items:flex-start; min-width:90px; transition:background .18s ease, transform .18s ease, box-shadow .18s ease; }
  .suggestion-btn:hover{ background:var(--accent,#3b6df0); color:#fff; transform:translateY(-2px); box-shadow:0 6px 14px rgba(0,0,0,.25); }
  .suggestion-btn strong{ font-size:12px; }
  .suggestion-btn span{ font-size:10px; opacity:.75; }
  .retry-btn{ cursor:pointer; background:var(--bg-alt,#222); color:inherit; border:1px solid var(--accent,#3b6df0); padding:6px 14px; border-radius:8px; font-size:12px; transition:all .18s ease; }
  .retry-btn:hover{ background:var(--accent,#3b6df0); color:#fff; transform:translateY(-2px); box-shadow:0 4px 12px rgba(59,109,240,.3); }
  /* Flip card (TWIN+ / TWIN*) */
  .flip-card{ position:relative; perspective:1200px; }
  .flip-inner{ position:relative; transition:transform .75s cubic-bezier(.68,-0.25,.32,1.25); transform-style:preserve-3d; }
  .flip-card.flipped .flip-inner{ transform:rotateY(180deg); }
  .face{ backface-visibility:hidden; position:relative; }
  .face.back{ position:absolute; inset:0; transform:rotateY(180deg); }
  .flip-badge{ font-size:10px; letter-spacing:.5px; text-transform:uppercase; opacity:.55; }
  .heavy-note{ font-size:11px; opacity:.75; margin-top:6px; }
  .flip-btn-small{ cursor:pointer; background:transparent; border:1px solid currentColor; padding:4px 8px; font-size:11px; border-radius:8px; opacity:.85; }
  .flip-btn-small:hover{ opacity:1; transform:translateY(-2px); }
  
  /* Universal fade-in animation for all panels */
  @keyframes fadeInUp{
    from{ opacity:0; transform: translateY(12px); }
    to  { opacity:1; transform: translateY(0); }
  }
  .bot, .user{ animation: fadeInUp 0.35s ease both; }
  
  /* Unified button style (Details, Explain, TWIN+) */
  .action-btn, .details-btn, .flip-btn{ 
    color: inherit; 
    background: transparent; 
    border:2px solid currentColor; 
    border-radius:10px; 
    padding:8px 16px; 
    font-weight:600; 
    cursor:pointer; 
    font-size:13px; 
    transition:all .18s ease;
    display:inline-block;
  }
  .action-btn:hover, .details-btn:hover, .flip-btn:hover{ 
    background: rgba(255,255,255,0.95); 
    color: var(--bg, #1a1a2e);
    transform:translateY(-3px); 
    box-shadow:0 8px 18px rgba(0,0,0,.3);
  }
  
  /* TWIN+ button (pink) */
  .plus-btn, .plus-btn-back{ 
    background: #ec4899 !important; 
    color: #fff !important; 
    border-color: #ec4899 !important;
  }
  .plus-btn:hover, .plus-btn-back:hover{ 
    background: #db2777 !important; 
    color: #fff !important; 
    border-color: #db2777 !important;
    transform:translateY(-3px); 
    box-shadow:0 8px 18px rgba(236,72,153,.4) !important;
  }
  /* Ensure TWIN* matches TWIN+ sizing exactly */
  .plus-btn, .plus-btn-back, .star-btn{
    padding: 8px 16px !important;
    font-size: 13px !important;
    border-width: 2px !important;
    border-radius: 10px !important;
    line-height: 1.2 !important;
  }
  
  /* Absolute parity for button height/shape across contexts */
  .action-btn.explain-btn,
  .action-btn.plus-btn,
  .action-btn.plus-btn-back,
  .action-btn.star-btn{
    padding: 8px 16px !important;
    font-size: 13px !important;
    height: auto !important;
    min-height: 40px !important;
    border-radius: 10px !important;
    border-width: 2px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
  }
  
  /* Card theme transformations */
  /* removed inner sky-blue flip styling: we tint the whole panel instead */
  /* When TWIN* is active, replace pink with clean sky-blue */
  .card-plus{ 
    position: relative; 
    overflow: hidden;
    transition: background 0.5s ease-in-out;
  }
  /* Flip-like animation for the whole panel (smoother) */
  @keyframes panel-flip {
    0%   { transform: perspective(1200px) rotateY(0); opacity: 1; }
    50%  { transform: perspective(1200px) rotateY(90deg); opacity: 0.85; }
    100% { transform: perspective(1200px) rotateY(0); opacity: 1; }
  }
  .card-plus.panel-flip{
    animation: panel-flip 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
    transform-style: preserve-3d;
  }
  
  /* Suggestions redesign */
  .suggestion-container{ 
    margin-top:12px; 
    animation: fadeInUp 0.35s ease both;
  }
  .suggestion-header{ 
    font-weight:700; 
    font-size:14px; 
    margin-bottom:10px;
    letter-spacing:0.3px;
  }
  .suggestions{ 
    display:flex; 
    flex-wrap:wrap; 
    gap:8px; 
    margin-bottom:12px;
  }
  .suggestion-chip{ 
    cursor:pointer; 
    background:rgba(255,255,255,0.08); 
    color:inherit; 
    border:1px solid currentColor; 
    padding:6px 12px; 
    border-radius:20px; 
    font-size:12px; 
    font-weight:500;
    transition:all .18s ease;
    display:flex;
    flex-direction:column;
    align-items:flex-start;
    min-width:100px;
  }
  .suggestion-chip:hover{ 
    background:var(--accent,#3b6df0); 
    color:#fff; 
    border-color:var(--accent,#3b6df0);
    transform:translateY(-3px); 
    box-shadow:0 6px 16px rgba(59,109,240,.4);
  }
  .suggestion-chip strong{ font-size:13px; font-weight:700; }
  .suggestion-chip span{ font-size:10px; opacity:.8; margin-top:2px; }
  
  .suggestion-retry-full{ 
    cursor:pointer; 
    background: rgba(255,255,255,0.05);
    color: inherit; 
    border: 1px solid rgba(255,255,255,0.2);
    padding: 10px 24px; 
    border-radius: 22px; 
    font-size: 13px; 
    font-weight: 600;
    transition: all 0.2s ease;
    width: 100%;
    text-align: center;
    backdrop-filter: blur(10px);
    margin-top: 12px;
  }
  .suggestion-retry-full:hover{ 
    background: rgba(255,255,255,0.12);
    border-color: rgba(255,255,255,0.4);
    transform: translateY(-2px); 
    box-shadow: 0 4px 12px rgba(255,255,255,0.15);
  }
  
  /* Circular flip button (top-right corner) */
  
  /* removed inner twin-star-theme: we style the outer panel instead */
  
  /* Leaderboard / Predictions Styles */
  .leaderboard-container{ padding: 8px 0; }
  .predictions-list{ max-height: 450px; overflow-y: auto; margin-bottom: 16px; }
  .prediction-card{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
  }
  .prediction-card:hover{
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.2);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }
  .pred-header{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }
  .pred-date{ opacity: 0.6; }
  .pred-body{ }
  .pred-row{
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    font-size: 14px;
  }
  .pred-row.small{ font-size: 12px; }
  .clear-predictions-btn{
    width: 100%;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid rgba(239,68,68,0.4);
    background: rgba(239,68,68,0.15);
    color: #f87171;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .clear-predictions-btn:hover{
    background: rgba(239,68,68,0.25);
    border-color: rgba(239,68,68,0.6);
    transform: translateY(-2px);
  }
  .save-btn{
    background: transparent !important;
    border-color: rgba(251,191,36,0.4) !important;
    color: #fbbf24 !important;
  }
  .save-btn:hover{
    background: rgba(251,191,36,0.15) !important;
    border-color: rgba(251,191,36,0.6) !important;
  }
  .save-btn:disabled{
    cursor: not-allowed !important;
    opacity: 0.5 !important;
  }
  
  /* Star save button styling - positioned in top right */
  .star-save-btn{
    position: absolute;
    top: 16px;
    right: 16px;
    background: transparent !important;
    border: none !important;
    color: #fbbf24 !important;
    padding: 0 !important;
    min-width: auto !important;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .star-save-btn:hover{
    transform: scale(1.2);
    filter: brightness(1.2);
  }
  .star-save-btn:disabled{
    cursor: not-allowed !important;
    opacity: 0.5 !important;
  }
  .star-save-btn i{
    font-size: 20px;
  }
  
  /* Feedback buttons in leaderboard */
  .pred-feedback{
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.1);
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .feedback-label{
    font-weight: 600;
    font-size: 13px;
    opacity: 0.9;
  }
  .feedback-buttons{
    display: flex;
    gap: 10px;
  }
  .feedback-btn{
    flex: 1;
    padding: 10px;
    border-radius: 10px;
    border: 2px solid;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
  }
  .feedback-yes-btn{
    background: rgba(74,222,128,0.15);
    border-color: rgba(74,222,128,0.4);
    color: #4ade80;
  }
  .feedback-yes-btn:hover{
    background: rgba(74,222,128,0.25);
    border-color: rgba(74,222,128,0.6);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(74,222,128,0.3);
  }
  .feedback-no-btn{
    background: rgba(248,113,113,0.15);
    border-color: rgba(248,113,113,0.4);
    color: #f87171;
  }
  .feedback-no-btn:hover{
    background: rgba(248,113,113,0.25);
    border-color: rgba(248,113,113,0.6);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(248,113,113,0.3);
  }
  .pred-feedback-complete{
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.1);
  }
  .feedback-result{
    font-weight: 600;
    font-size: 13px;
  }
  .feedback-yes-text{
    color: #4ade80;
  }
  .feedback-no-text{
    color: #f87171;
  }
  .prediction-card.feedback-yes{
    border-left: 4px solid #4ade80;
  }
  .prediction-card.feedback-no{
    border-left: 4px solid #f87171;
  }
  
  /* Thank you message animation */
  @keyframes fadeInScale{
    from{ opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
    to{ opacity: 1; transform: translate(-50%, -50%) scale(1); }
  }
  @keyframes fadeOutScale{
    from{ opacity: 1; transform: translate(-50%, -50%) scale(1); }
    to{ opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
  }
  
  /* Inaccuracy modal input styling */
  .inaccuracy-form input:focus,
  .inaccuracy-form textarea:focus {
    border-color: rgba(59,130,246,0.6) !important;
    background: rgba(59,130,246,0.05) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
  }
  .inaccuracy-form input::placeholder,
  .inaccuracy-form textarea::placeholder {
    color: rgba(255,255,255,0.4);
  }
  #submitInaccuracy:hover {
    background: #dc2626 !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(239,68,68,0.4);
  }
  #cancelInaccuracy:hover {
    background: rgba(255,255,255,0.05);
    border-color: rgba(255,255,255,0.5);
    transform: translateY(-2px);
  }
  `;
  const tag = document.createElement('style');
  tag.setAttribute('data-twin-explain-css','1');
  tag.textContent = css;
  document.head.appendChild(tag);
})();


document.addEventListener('DOMContentLoaded', () => {
  const inputEl = document.getElementById('userInput');
  if (!inputEl) return;

  // Only restore query if returning from predictions (not a fresh session)
  const fromPredictions = document.referrer.includes('predictions.html');
  const savedQuery = localStorage.getItem('twin_last_query');
  if (savedQuery && fromPredictions) {
    inputEl.value = savedQuery;
  } else if (!fromPredictions) {
    // Fresh session - clear the saved query
    localStorage.removeItem('twin_last_query');
  }

  // Save query to localStorage on input change (debounced)
  let saveTimeout;
  inputEl.addEventListener('input', () => {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
      const currentValue = inputEl.value.trim();
      if (currentValue) {
        localStorage.setItem('twin_last_query', currentValue);
      }
    }, 500); // Save after 500ms of no typing
  });

  inputEl.addEventListener('keydown', (e) => {
    if (e.isComposing) return; // ignore IME composition
    const val = (inputEl.value || '').trim();

    // Tab key => clear chat
    if (e.key === 'Tab') {
      e.preventDefault();
      clearChat();
      return;
    }

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


function prettyMethodName(m){
  if(!m) return '';
  return m.replace(/_/g,' ') // underscores to spaces
          .replace(/\b\w/g, c => c.toUpperCase()) // capitalize each word
          .replace(/ema/i,'EMA')
          .replace(/dma/i,'DMA')
          .replace(/\bma\b/i,'MA')
          .replace(/Mean Reversion/i,'Mean Reversion')
          .replace(/Linear Trend/i,'Linear Trend')
          .replace(/Trend Blend/i,'Trend Blend')
          .replace(/drift/i,'Drift');
}

async function updateExistingForecast(bot, newMethod, query) {
  console.log('Updating existing forecast with method:', newMethod);
  
  try {
    // Add loading indicator to existing bot
    bot.style.opacity = '0.6';
    
    const url = 'http://localhost:5000/predict';
    const payload = { input: `${query}`, method: newMethod };
    
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    if (!r.ok) {
      throw new Error(`HTTP ${r.status}`);
    }
    
    const data = await r.json();
    bot.style.opacity = '1';
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    // Update the content of the existing bot
    const delta = data.result - data.lastClose;
    const pct   = (delta / data.lastClose) * 100;
    const sign  = delta >= 0 ? '+' : '';
    const methods = ['ema_drift','linear_trend','mean_reversion','trend_blend'];
    const methodButtons = methods.map(m => `
      <button class="method-btn ${m === data.method ? 'active' : ''}" data-method="${m}" title="Switch to ${prettyMethodName(m)}">${prettyMethodName(m)}</button>
    `).join('');
    const methodToggle = `<span class="method-toggle" role="button" aria-expanded="false" title="Change equation">Method: ${prettyMethodName(data.method)} · drift/day: ${Number(data.drift_per_day).toFixed(4)} ▾</span>`;
    const backtestRow = data.backtest ? `
      <div class="backtest-row muted">Backtest: MAE ≈ <strong>$${data.backtest.mae.toFixed(2)}</strong> (120 days, ${data.duration} horizon)</div>
    ` : '';
    // Only show star button if logged in
    const isLoggedIn = localStorage.getItem('twin_user_logged_in') === 'true';
    const starButtonHTML = isLoggedIn ? `
      <button class="action-btn star-save-btn" type="button" title="Save this prediction" data-pred-id="${Date.now()}">
        <i class="far fa-star"></i>
      </button>
    ` : '';
    
    // Add company logo
    const logoHTML = `
      <img src="https://logo.clearbit.com/${getCompanyDomain(data.stock)}" 
           alt="${data.stock}" 
           class="stock-logo" 
           onerror="this.style.display='none'"
           style="width:32px;height:32px;border-radius:6px;margin-right:8px;vertical-align:middle;">
    `;
    
    bot.innerHTML = `
      ${starButtonHTML}
      <div class="title">${logoHTML}${data.stock}${data.duration ? ' in ' + data.duration : ''}</div>
      <div>Last close: <strong>$${data.lastClose.toFixed(2)}</strong></div>
      <div>Forecasted price: <strong>$${data.result.toFixed(2)}</strong>
        <span class="${delta>=0 ? 'up' : 'down'}">(${sign}${delta.toFixed(2)} | ${sign}${pct.toFixed(2)}%)</span>
      </div>
        <div class="method-row">
          ${methodToggle}
          <div class="method-menu hidden">${methodButtons}</div>
        </div>
      <div class="sparkline"></div>
      <div class="btnrow">
        <button class="action-btn explain-btn" type="button">Explain</button>
  <button class="action-btn plus-btn" type="button">TWIN+</button>
      </div>
      ${backtestRow}
      <div class="explain hidden"></div>
    `;
    
    // Re-attach all event listeners
    const pane = document.getElementById('messages-basic');
    attachExplain(bot.querySelector('.explain-btn'), bot.querySelector('.explain'), {
      mode:'forecast', stock:data.stock, duration:data.duration,
      lastClose:data.lastClose, result:data.result,
      delta:delta, pct:pct, method:data.method, driftPerDay:data.drift_per_day,
      backtest:data.backtest || null
    });
    
  bot.querySelector('.plus-btn').addEventListener('click', () => sendPlus(query));
    
    // Re-wire method toggle and buttons
    const toggleEl = bot.querySelector('.method-toggle');
    const menuEl = bot.querySelector('.method-menu');
    toggleEl.addEventListener('click', () => {
      // Subtle, smooth tap animation (no spin)
      toggleEl.classList.remove('tap'); // reset if still present
      void toggleEl.offsetWidth; // reflow to allow retrigger
      toggleEl.classList.add('tap');

      const hidden = menuEl.classList.contains('hidden');
      if (hidden){
        menuEl.classList.remove('hidden');
        toggleEl.setAttribute('aria-expanded','true');
        toggleEl.textContent = `Method: ${prettyMethodName(data.method)} · drift/day: ${Number(data.drift_per_day).toFixed(4)} ▴`;
      } else {
        menuEl.classList.add('hidden');
        toggleEl.setAttribute('aria-expanded','false');
        toggleEl.textContent = `Method: ${prettyMethodName(data.method)} · drift/day: ${Number(data.drift_per_day).toFixed(4)} ▾`;
      }
      scrollDown(pane,true);
    });
    // Clean up class after animation ends
    toggleEl.addEventListener('animationend', (e) => {
      if (e.animationName === 'method-tap') {
        toggleEl.classList.remove('tap');
      }
    });
    
    menuEl.querySelectorAll('.method-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const selectedMethod = btn.getAttribute('data-method');
        if (!selectedMethod || selectedMethod === data.method) return;
        updateExistingForecast(bot, selectedMethod, query);
      });
    });
    
    renderSparkline(data.stock, bot.querySelector('.sparkline'));
    
  } catch (e) {
    console.error('Error updating forecast:', e);
    bot.style.opacity = '1';
    // Show error in the existing bot instead of creating new one
    bot.innerHTML = `<div class="muted">Error updating forecast: ${e.message}</div>`;
  }
}

// Query blocking - prevent duplicate TWIN- queries
let isBasicQueryRunning = false;

async function sendBasic(methodOverride = null, reusedQuery = null) {
  console.log('sendBasic() called');
  
  // Block if a TWIN- query is already running
  if (isBasicQueryRunning) {
    console.log('TWIN- query already running, blocking duplicate request');
    return;
  }
  
  const inputEl = document.getElementById('userInput');
  const q = (reusedQuery != null ? reusedQuery : (inputEl.value || '')).trim();
  if (!q) {
    console.log('No input provided');
    return;
  }
  
  isBasicQueryRunning = true;
  console.log('Input:', q);
  const pane = document.getElementById('messages-basic');
  if (!pane) {
    console.error('messages-basic element not found');
    return;
  }

  const user = document.createElement('div');
  user.className = 'user';
  user.textContent = q.endsWith('?') ? q : `${q}?`;
  fade(user);
  pane.appendChild(user);
  scrollDown(pane, true);

  const loading = addLoading(pane);

  try {
    console.log('Fetching from:', 'http://localhost:5000/predict');
    // FETCH UNCHANGED
    const r = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: q, method: methodOverride || undefined })
    });
    console.log('Fetch response status:', r.status);
    const data = await r.json();
    console.log('Fetch response data:', data);
    pane.removeChild(loading);

    const bot = document.createElement('div');
    bot.className = 'bot';

    if (!r.ok || data.error) {
      let html = '';
      if (data.suggestions && Array.isArray(data.suggestions) && data.suggestions.length){
        html += '<div class="suggestion-container">';
        html += '<div class="suggestion-header">Did you mean?</div>';
        html += '<div class="suggestions">' + data.suggestions.map(s => `
          <button class="suggestion-chip" data-echo="${s.echo}" data-symbol="${s.symbol}" title="Use ${s.symbol}">
            <strong>${s.symbol}</strong><span>${s.name}</span>
          </button>`).join('') + '</div>';
        html += '<button class="suggestion-retry-full" data-action="retry">Retry</button>';
        html += '</div>';
      } else {
        const errMsg = data.error || 'Request failed';
        html = `<div class="muted">${errMsg}</div>`;
      }
      bot.innerHTML = html;
      fade(bot); pane.appendChild(bot); scrollDown(pane, true);
      
      // Suggestion chip clicks - clear suggestions and rerun query
      bot.querySelectorAll('.suggestion-chip').forEach(btn => {
        btn.addEventListener('click', () => {
          const echo = btn.getAttribute('data-echo');
          if (echo){
            // Clear the suggestion display
            bot.remove();
            // Set input and rerun
            inputEl.value = echo;
            sendBasic(null, echo);
          }
        });
      });
      
      // Retry button - restore original input
      const retryBtn = bot.querySelector('.suggestion-retry-full');
      if (retryBtn) {
        retryBtn.addEventListener('click', () => {
          inputEl.value = q;
          inputEl.focus();
          inputEl.select();
        });
      }
      inputEl.value = ''; return;
    }

    // Price-only (no timeframe)
    if (data.mode === 'price_only' || data.result === undefined) {
      // Only show star button if logged in (even for price-only)
      const isLoggedIn = localStorage.getItem('twin_user_logged_in') === 'true';
      const starButtonHTML = isLoggedIn ? `
        <button class="action-btn star-save-btn" type="button" title="Save this query" data-pred-id="${Date.now()}">
          <i class="far fa-star"></i>
        </button>
      ` : '';
      bot.innerHTML = `
        ${starButtonHTML}
        <div class="title">${data.stock}</div>
        <div>Current (last close): <strong>$${Number(data.lastClose).toFixed(2)}</strong></div>
        <div class="muted">${data.message || "Add a timeframe (e.g., 'in 3 days') to get a forecast."}</div>
        <div class="sparkline"></div>
        <div class="btnrow">
          <button class="action-btn explain-btn" type="button">Explain</button>
          <button class="action-btn plus-btn" type="button">TWIN+</button>
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
      const methods = ['ema_drift','linear_trend','mean_reversion','trend_blend']; // include trend_blend placeholder
      const methodButtons = methods.map(m => `
        <button class="method-btn ${m === data.method ? 'active' : ''}" data-method="${m}" title="Switch to ${prettyMethodName(m)}">${prettyMethodName(m)}</button>
      `).join('');
      // Collapsible method menu per spec with drift/day inline
      const methodToggle = `<span class="method-toggle" role="button" aria-expanded="false" title="Change equation">Method: ${prettyMethodName(data.method)} · drift/day: ${Number(data.drift_per_day).toFixed(4)} ▾</span>`;
    const backtestRow = data.backtest ? `
      <div class="backtest-row muted">Backtest: MAE ≈ <strong>$${data.backtest.mae.toFixed(2)}</strong> (120 days, ${data.duration} horizon)</div>
    ` : '';
    // Only show star button if logged in
    const isLoggedIn = localStorage.getItem('twin_user_logged_in') === 'true';
    const starButtonHTML = isLoggedIn ? `
      <button class="action-btn star-save-btn" type="button" title="Save this prediction" data-pred-id="${Date.now()}">
        <i class="far fa-star"></i>
      </button>
    ` : '';
    bot.innerHTML = `
      ${starButtonHTML}
      <div class="title">${data.stock}${data.duration ? ' in ' + data.duration : ''}</div>
      <div>Last close: <strong>$${data.lastClose.toFixed(2)}</strong></div>
      <div>Forecasted price: <strong>$${data.result.toFixed(2)}</strong>
        <span class="${delta>=0 ? 'up' : 'down'}">(${sign}${delta.toFixed(2)} | ${sign}${pct.toFixed(2)}%)</span>
      </div>
        <div class="method-row">
          ${methodToggle}
          <div class="method-menu hidden">${methodButtons}</div>
        </div>
      <div class="sparkline"></div>
      <div class="btnrow">
        <button class="action-btn explain-btn" type="button">Explain</button>
  <button class="action-btn plus-btn" type="button">TWIN+</button>
      </div>
      ${backtestRow}
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
    
    // Wire star save button
    const saveBtn = bot.querySelector('.star-save-btn');
    if (saveBtn) {
      const predId = saveBtn.getAttribute('data-pred-id');
      const starIcon = saveBtn.querySelector('i');
      
      // Check if this prediction is already saved
      getSavedPredictions().then(savedPredictions => {
        const isSaved = savedPredictions.some(p => p.id == predId);
        if (isSaved) {
          // Mark as saved
          starIcon.className = 'fas fa-star';
          saveBtn.disabled = true;
          saveBtn.style.opacity = '0.6';
          saveBtn.style.cursor = 'not-allowed';
          saveBtn.title = 'Prediction saved';
        }
      });
      
      saveBtn.addEventListener('click', async () => {
        const predId = saveBtn.getAttribute('data-pred-id');
        const isStarred = saveBtn.disabled; // If disabled, it's already starred
        const starIcon = saveBtn.querySelector('i');
        
        if (isStarred) {
          // UNSTAR - Remove from predictions
          const token = localStorage.getItem('twin_supabase_token');
          
          if (token) {
            // Remove from database
            try {
              const response = await fetch(`/api/predictions/delete/${predId}`, {
                method: 'DELETE',
                headers: {
                  'Authorization': `Bearer ${token}`
                }
              });
              
              if (response.ok) {
                console.log('Prediction removed from database');
              }
            } catch (error) {
              console.error('Error removing prediction:', error);
            }
          }
          
          // Remove from localStorage
          const saved = JSON.parse(localStorage.getItem('twin_predictions') || '[]');
          const filtered = saved.filter(p => p.id != predId);
          localStorage.setItem('twin_predictions', JSON.stringify(filtered));
          
          // Reset star to empty
          starIcon.className = 'far fa-star';
          saveBtn.disabled = false;
          saveBtn.style.opacity = '1';
          saveBtn.style.cursor = 'pointer';
          saveBtn.title = 'Save this prediction';
          console.log('Prediction unstarred');
        } else {
          // STAR - Save prediction
          savePrediction({
            id: predId,
            stock: data.stock,
            duration: data.duration,
            lastClose: data.lastClose,
            predictedPrice: data.result,
            method: data.method,
            timestamp: new Date().toISOString(),
            delta: delta,
            pct: pct
          });
          
          // Fill the star
          starIcon.className = 'fas fa-star';
          saveBtn.disabled = true;
          saveBtn.style.opacity = '0.6';
          saveBtn.style.cursor = 'not-allowed';
          saveBtn.title = 'Prediction saved';
        }
      });
    }
    // Wire method buttons for re-forecasting without duplicating user text entry
    // Toggle open/close of method menu
    const toggleEl = bot.querySelector('.method-toggle');
    const menuEl = bot.querySelector('.method-menu');
    toggleEl.addEventListener('click', () => {
      // Subtle, smooth tap animation (no spin)
      toggleEl.classList.remove('tap'); // reset if still present
      void toggleEl.offsetWidth; // reflow to allow retrigger
      toggleEl.classList.add('tap');
      
      const hidden = menuEl.classList.contains('hidden');
      if (hidden){
        menuEl.classList.remove('hidden');
        toggleEl.setAttribute('aria-expanded','true');
        toggleEl.textContent = `Method: ${prettyMethodName(data.method)} · drift/day: ${Number(data.drift_per_day).toFixed(4)} ▴`;
      } else {
        menuEl.classList.add('hidden');
        toggleEl.setAttribute('aria-expanded','false');
        toggleEl.textContent = `Method: ${prettyMethodName(data.method)} · drift/day: ${Number(data.drift_per_day).toFixed(4)} ▾`;
      }
      scrollDown(pane,true);
    });
    // Clean up class after animation ends
    toggleEl.addEventListener('animationend', (e) => {
      if (e.animationName === 'method-tap') {
        toggleEl.classList.remove('tap');
      }
    });
    // Wire method buttons for re-forecasting without duplicating user text entry
    menuEl.querySelectorAll('.method-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const newMethod = btn.getAttribute('data-method');
        if (!newMethod || newMethod === data.method) return;
        
        // Remove the current bot message to replace it with loading
        if (bot && bot.parentNode) {
          bot.parentNode.removeChild(bot);
        }
        
        // Make fresh API call with the new method
        sendBasic(newMethod, q);
      });
    });
    renderSparkline(data.stock, bot.querySelector('.sparkline'));

  } catch (e) {
    console.error('Error in sendBasic:', e);
    pane.removeChild(loading);
    const bot = document.createElement('div'); bot.className = 'bot';
    bot.textContent = 'Error: ' + e.message; fade(bot); pane.appendChild(bot); scrollDown(pane, true);
  } finally {
    // Always release the query lock
    isBasicQueryRunning = false;
  }

  inputEl.value = '';
}


async function sendPlus(queryFromTwin = null) {
  console.log('sendPlus() called with:', queryFromTwin);
  const inputEl = document.getElementById('userInput');
  const raw = (queryFromTwin ?? inputEl.value);
  const q = (raw || '').trim();
  if (!q) {
    console.log('No input in sendPlus');
    return;
  }

  console.log('sendPlus input:', q);
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
    console.log('Fetching TWIN+ from:', 'http://localhost:5000/predict_plus');
    // FETCH UNCHANGED
    const r = await fetch('http://localhost:5000/predict_plus', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: q })
    });
    console.log('TWIN+ response status:', r.status);
    const data = await r.json();
    console.log('TWIN+ response data:', data);
    pane.removeChild(loading);

    const bot = document.createElement('div');
    bot.className = 'bot';

    if (!r.ok || data.error) {
      let html = '';
      if (data.suggestions && Array.isArray(data.suggestions) && data.suggestions.length){
        html += '<div class="suggestion-container">';
        html += '<div class="suggestion-header">Did you mean?</div>';
        html += '<div class="suggestions">' + data.suggestions.map(s => `
          <button class="suggestion-chip" data-echo="${s.echo}" data-symbol="${s.symbol}" title="Use ${s.symbol}">
            <strong>${s.symbol}</strong><span>${s.name}</span>
          </button>`).join('') + '</div>';
        html += '<button class="suggestion-retry-full" data-action="retry">Retry</button>';
        html += '</div>';
      } else {
        const errMsg = data.error || 'Request failed';
        html = `<div class="muted">${errMsg}</div>`;
      }
      bot.innerHTML = html;
      fade(bot); pane.appendChild(bot); scrollDown(pane, true);
      
      // Suggestion chip clicks - clear suggestions and rerun query
      bot.querySelectorAll('.suggestion-chip').forEach(btn => {
        btn.addEventListener('click', () => {
          const echo = btn.getAttribute('data-echo');
          if (echo){
            // Clear the suggestion display
            bot.remove();
            // Set input and rerun
            const inputEl2 = document.getElementById('userInput');
            inputEl2.value = echo;
            sendPlus(echo);
          }
        });
      });
      
      // Retry button
      const retryBtn = bot.querySelector('.suggestion-retry-full');
      if (retryBtn) {
        retryBtn.addEventListener('click', () => {
          const inputEl2 = document.getElementById('userInput');
          inputEl2.value = q;
          inputEl2.focus();
          inputEl2.select();
        });
      }
      return;
    }

    const d = data.diagnostics || {};
    const hasForecast = (data.result !== undefined) && (data.lastClose !== undefined);
    let forecastBlock = '';
    if (hasForecast){
      const delta = data.result - data.lastClose;
      const pct = (delta / data.lastClose) * 100;
      const sign = delta >= 0 ? '+' : '';
      forecastBlock = `
        <div>Forecasted price: <strong>$${data.result.toFixed(2)}</strong>
          <span class="${delta>=0 ? 'up':'down'}">(${sign}${delta.toFixed(2)} | ${sign}${pct.toFixed(2)}%)</span>
        </div>
        <div class="method-row">
          <span class="muted">Method: ${prettyMethodName(data.method || 'light_ml_v1')} · drift/day: ${Number(data.drift_per_day).toFixed(4)}</span>
        </div>
      `;
    }
    const voltxt  = d.ann_vol_forecast != null ? `${(d.ann_vol_forecast*100).toFixed(1)}%` : 'n/a';
    const sizetxt = d.position_size != null ? `${(d.position_size*100).toFixed(0)}%` : 'n/a';
    const rangeTxt = (d.donchian50_lo != null && d.donchian50_hi != null)
      ? ` (range ${d.donchian50_lo?.toFixed(2)}–${d.donchian50_hi?.toFixed(2)})`
      : '';

    const summaryLine = `<div class="plus-summary muted"><strong>${data.method.replace('_',' ')}</strong> | Momentum ${(d.momentum_12m*100).toFixed(1)}% | Vol ${voltxt} | Size ${sizetxt}</div>`;

    bot.innerHTML = `
      <div class="flip-card">
        <div class="flip-inner">
          <div class="face front">
            <div class="title">${data.stock}${data.duration ? ' in ' + data.duration : ''}</div>
            <div>Last close: <strong>$${data.lastClose ? data.lastClose.toFixed(2) : 'N/A'}</strong></div>
            ${forecastBlock}
            ${summaryLine}
            <div class="sparkline"></div>
            <div class="btnrow">
              <button class="action-btn explain-btn" type="button">Explain</button>
              <button class="action-btn star-btn" type="button" title="Switch to TWIN* (heavy ML)" aria-label="Switch to TWIN* model">TWIN*</button>
            </div>
            <div class="explain hidden"></div>
          </div>
          <div class="face back">
            <div class="flip-badge">TWIN*</div>
            <div class="title">${data.stock}${data.duration ? ' in ' + data.duration : ''}</div>
            <div class="muted">Heavy ML Ensemble</div>
            <div id="twin-star-forecast" class="muted">Loading ensemble forecast...</div>
            <div class="btnrow">
              <button class="action-btn explain-btn" type="button">Explain</button>
              <button class="action-btn plus-btn-back" type="button" title="Back to TWIN+" aria-label="Switch back to TWIN+">TWIN+</button>
            </div>
            <div class="explain hidden"></div>
          </div>
        </div>
      </div>
    `;
    fade(bot); pane.appendChild(bot); scrollDown(pane, true);

    // Render sparkline for TWIN+ front face
    const sparklineContainer = bot.querySelector('.front .sparkline');
    if (sparklineContainer) {
      renderSparkline(data.stock, sparklineContainer);
    }

    // Flip handling with TWIN* API call
  const flipCard = bot.querySelector('.flip-card');
  const flipBtnFront = bot.querySelector('.star-btn');
  const flipBtnBack = bot.querySelector('.plus-btn-back');
  const cardContainer = pane.closest('.card');
    if (flipBtnFront) {
      flipBtnFront.addEventListener('click', async () => {
        flipCard.classList.add('flipped');
        // Don't tint inner content, only the outer card
        if (cardContainer) {
          cardContainer.classList.add('twin-star-active');
          cardContainer.classList.add('panel-flip');
          const onAnimEnd = () => {
            cardContainer.classList.remove('panel-flip');
            cardContainer.removeEventListener('animationend', onAnimEnd);
          };
          cardContainer.addEventListener('animationend', onAnimEnd);
        }
        scrollDown(pane,true);
        
        // Call TWIN* API
        const starForecastDiv = bot.querySelector('#twin-star-forecast');
        if (starForecastDiv) {
          starForecastDiv.textContent = 'Loading ensemble forecast...';
          try {
            const r = await fetch('/predict_star', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ input: q })
            });
            const starData = await r.json();
            if (r.ok && starData.result) {
              const delta = starData.result - starData.lastClose;
              const pct = (delta / starData.lastClose) * 100;
              const sign = delta >= 0 ? '+' : '';
              starForecastDiv.innerHTML = `
                <div>Last close: <strong>$${starData.lastClose.toFixed(2)}</strong></div>
                <div>Forecasted price: <strong>$${starData.result.toFixed(2)}</strong>
                  <span class="${delta>=0 ? 'up':'down'}">(${sign}${delta.toFixed(2)} | ${sign}${pct.toFixed(2)}%)</span>
                </div>
                <div class="muted small" style="margin-top:8px">Method: ${starData.method || 'ensemble'} · drift/day: ${starData.drift_per_day.toFixed(4)}</div>
              `;
            } else {
              starForecastDiv.textContent = starData.error || 'TWIN* model not available yet';
            }
          } catch (err) {
            starForecastDiv.textContent = 'Failed to load TWIN* forecast';
          }
        }
      });
    }
    if (flipBtnBack) {
      flipBtnBack.addEventListener('click', () => {
        flipCard.classList.remove('flipped');
        if (cardContainer) {
          // animate the panel flip on the way back as well
          cardContainer.classList.add('panel-flip');
          const onAnimEnd = () => {
            cardContainer.classList.remove('panel-flip');
            cardContainer.classList.remove('twin-star-active');
            cardContainer.removeEventListener('animationend', onAnimEnd);
          };
          cardContainer.addEventListener('animationend', onAnimEnd);
        }
        scrollDown(pane,true);
      });
    }

    // Explain panel wiring
    // Explain for front face
    const explainPanelFront = bot.querySelector('.front .explain');
    const explainBtnFront = bot.querySelector('.front .explain-btn');
    if (explainPanelFront && explainBtnFront){
      attachExplain(explainBtnFront, explainPanelFront, {
        mode: 'plus',
        decision: data.decision,
        diagnostics: d
      });
    }
    // Explain for back face (reuse diagnostics)
    const explainPanelBack = bot.querySelector('.back .explain');
    const explainBtnBack = bot.querySelector('.back .explain-btn');
    if (explainPanelBack && explainBtnBack){
      attachExplain(explainBtnBack, explainPanelBack, {
        mode: 'plus',
        decision: data.decision,
        diagnostics: d
      });
    }

   

  } catch (e) {
    console.error('Error in sendPlus:', e);
    pane.removeChild(loading);
    const bot = document.createElement('div'); bot.className = 'bot';
    bot.textContent = 'Error: ' + e.message; fade(bot); pane.appendChild(bot); scrollDown(pane, true);
  }
}



async function sendTwin(){
  console.log('sendTwin() called');
  const q = (document.getElementById('userInput').value || '').trim();
  if (!q) {
    console.log('No input in sendTwin');
    return;
  }
  console.log('sendTwin input:', q);
  await sendBasic();
  if (hasDuration(q)) {
    console.log('Duration detected, calling sendPlus');
    await sendPlus(q);
  } else {
    console.log('No duration detected');
    const pane = document.getElementById('messages-plus');
    const note = document.createElement('div');
    note.className = 'bot';
    note.innerHTML = `
      <div class="title">Need a timeframe</div>
      <div class="muted">To run TWIN+ alongside TWIN-, add a horizon, e.g., "${q} in 3 days".</div>
    `;
    fade(note); pane.appendChild(note); scrollDown(pane, true);
  }
}

// Make functions globally accessible for onclick handlers
window.sendBasic = sendBasic;
window.sendTwin = sendTwin;
window.sendPlus = sendPlus;
window.selectStock = selectStock;
window.selectDuration = selectDuration;

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
    
    <h4 class="explain-title" style="margin-top:16px;">Technical Details</h4>
    <ul class="metrics-list">
      <li><strong>12m momentum:</strong> ${(data.diagnostics?.momentum_12m*100)?.toFixed(2) || 'n/a'}%</li>
      <li><strong>50/200 DMA slope:</strong> ${data.diagnostics?.dma50_slope?.toFixed(4) || 'n/a'} / ${data.diagnostics?.dma200_slope?.toFixed(4) || 'n/a'}</li>
      <li><strong>Donchian 50:</strong> ${data.diagnostics?.donchian50_breakout ? 'BREAKOUT' : 'range'}${(data.diagnostics?.donchian50_lo && data.diagnostics?.donchian50_hi) ? ` (range ${data.diagnostics.donchian50_lo?.toFixed(2)}–${data.diagnostics.donchian50_hi?.toFixed(2)})` : ''}</li>
      <li><strong>Annualized vol (HAR-RV):</strong> ${data.diagnostics?.ann_vol_forecast ? `${(data.diagnostics.ann_vol_forecast*100).toFixed(1)}%` : 'n/a'}</li>
      <li><strong>Position size @ ${data.diagnostics?.target_vol ? (data.diagnostics.target_vol*100).toFixed(0) : '20'}% target vol:</strong> ${data.diagnostics?.position_size ? `${(data.diagnostics.position_size*100).toFixed(0)}%` : 'n/a'}</li>
    </ul>
    <div class="explain-actions">
      <button class="xlate" type="button" aria-expanded="false" style="color: inherit">Translate</button>
      <button class="copy-btn" type="button" title="Copy explanation to clipboard">
        <i class="fas fa-copy"></i> Copy
      </button>
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
            <button class="copy-btn" type="button" title="Copy explanation to clipboard">
              <i class="fas fa-copy"></i> Copy
            </button>
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

      // Add copy functionality
      panel.querySelectorAll('.copy-btn').forEach(copyBtn => {
        copyBtn.addEventListener('click', async () => {
          const textContent = panel.innerText || panel.textContent;
          try {
            await navigator.clipboard.writeText(textContent);
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            copyBtn.style.background = 'rgba(34, 197, 94, 0.2)';
            copyBtn.style.borderColor = 'rgba(34, 197, 94, 0.4)';
            setTimeout(() => {
              copyBtn.innerHTML = originalHTML;
              copyBtn.style.background = '';
              copyBtn.style.borderColor = '';
            }, 2000);
          } catch (err) {
            console.error('Failed to copy:', err);
            copyBtn.innerHTML = '<i class="fas fa-times"></i> Failed';
            setTimeout(() => {
              copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
            }, 2000);
          }
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

// Menu handling is provided by `theme-toggle.js` (initMenu). Removed duplicate handlers to avoid
// conflicting listeners which caused immediate open/close toggles when clicking the menu button.

// Clear chat function - clears both TWIN- and TWIN+ panels
function clearChat() {
  const basicPane = document.getElementById('messages-basic');
  const plusPane = document.getElementById('messages-plus');
  
  if (basicPane) {
    basicPane.innerHTML = '';
  }
  if (plusPane) {
    plusPane.innerHTML = '';
  }
  
  console.log('Chat cleared');
}

// Make clearChat globally accessible
window.clearChat = clearChat;


