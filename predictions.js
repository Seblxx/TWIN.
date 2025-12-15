// Predictions.js - Card expansion and feedback system
const THEMES = [
  { name: 'Royal', file: 'royal.css', color: 'linear-gradient(135deg, #1e3a8a, #3b82f6)' },
  { name: 'Dark', file: 'dark.css', color: '#1a1a2e' },
  { name: 'Light', file: 'light.css', color: '#f0f0f0' },
  { name: 'Monochrome', file: 'monochrome.css', color: '#1e3a5f' },
  { name: 'Liquid Glass', file: 'liquidglass.css', color: '#000000' }
];

let currentThemeIndex = 0;
let currentPredictions = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  loadPredictions();
  setupEventListeners();
  console.log('Predictions page initialized');
});

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem('twin_theme_css') || 'dark.css';
  console.log('Loading theme:', savedTheme);
  const themeIndex = THEMES.findIndex(t => t.file === savedTheme);
  currentThemeIndex = themeIndex >= 0 ? themeIndex : 0;
  setTheme(THEMES[currentThemeIndex].file);
}

function setTheme(cssFile) {
  const link = document.getElementById('themeCss');
  link.href = cssFile + '?v=15';
  updateThemeButton(cssFile);
  localStorage.setItem('twin_theme_css', cssFile);
}

function updateThemeButton(cssFile) {
  const btn = document.getElementById('themeToggle');
  const theme = THEMES.find(t => t.file === cssFile);
  if (theme) {
    btn.style.background = theme.color;
  }
}

function cycleTheme() {
  currentThemeIndex = (currentThemeIndex + 1) % THEMES.length;
  setTheme(THEMES[currentThemeIndex].file);
}

// Get predictions from backend or localStorage
async function getPredictions() {
  try {
    const userEmail = localStorage.getItem('twin_user_email') || 'guest';
    const token = localStorage.getItem('twin_supabase_token');
    
    // If guest or no token, use localStorage
    if (userEmail === 'guest' || !token) {
      return JSON.parse(localStorage.getItem('twin_predictions') || '[]');
    }
    
    // Fetch from backend for authenticated users with token
    const response = await fetch('/api/predictions/user', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    
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
  } catch (error) {
    // Suppress fetch errors during logout/navigation transitions
    if (error.message !== 'Failed to fetch' && error.name !== 'TypeError') {
      console.error('Error fetching predictions:', error);
    }
    // Fallback to localStorage
    return JSON.parse(localStorage.getItem('twin_predictions') || '[]');
  }
}

// Format timestamp
function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = date.getHours();
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const ampm = hours >= 12 ? 'p.m.' : 'a.m.';
  const displayHours = hours % 12 || 12;
  
  return `${date.getFullYear()}-${month}-${day}<br>${displayHours}:${minutes} ${ampm}`;
}

// Display predictions from current array (no fetch)
function displayPredictions() {
  const list = document.getElementById('predictionsList');
  const countEl = document.getElementById('predictionsCount');
  
  // Update count
  countEl.textContent = `${currentPredictions.length} PREDICTION${currentPredictions.length !== 1 ? 'S' : ''}`;
  
  if (currentPredictions.length === 0) {
    list.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-chart-line"></i>
        <h3>No predictions yet</h3>
        <p>Save a prediction using the star icon on index.html</p>
      </div>
    `;
    return;
  }

  // Render compact cards (ticker, duration, current price, predicted price only)
  list.innerHTML = currentPredictions.map((pred, index) => {
    return `
      <div class="prediction-item" onclick="expandPrediction(${index})">
        <div class="item-header">
          <div class="item-left">
            <div class="stock-symbol">${pred.stock}</div>
            <div class="duration-badge">${pred.duration}</div>
          </div>
        </div>
        
        <div class="item-content">
          <div class="stat-item">
            <div class="stat-label">CURRENT</div>
            <div class="stat-value">$${pred.lastClose.toFixed(2)}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">PREDICTED</div>
            <div class="stat-value">$${pred.predictedPrice.toFixed(2)}</div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Load and display predictions from backend/storage
async function loadPredictions() {
  currentPredictions = await getPredictions();
  console.log('Loading predictions...');
  console.log('Raw localStorage:', localStorage.getItem('twin_predictions'));
  console.log('Parsed predictions:', currentPredictions);
  console.log('Number of predictions:', currentPredictions.length);
  displayPredictions();
}

// Expand prediction with detailed view and feedback options
function expandPrediction(index) {
  const pred = currentPredictions[index];
  if (!pred) return;

  const change = pred.predictedPrice - pred.lastClose;
  const changePercent = ((change / pred.lastClose) * 100).toFixed(2);
  const isPositive = change >= 0;

  const overlay = document.getElementById('expansionOverlay');
  
  // Create expanded card HTML
  const expandedHTML = `
    <div class="expanded-card">
      <button class="close-btn" onclick="closeExpansion()">
        <i class="fas fa-times"></i>
      </button>
      
      <div class="expanded-header">
        <div class="stock-symbol">${pred.stock}</div>
        <div class="duration-badge">${pred.duration}</div>
      </div>
      
      <div class="expanded-stats">
        <div class="expanded-stat">
          <div class="expanded-stat-label">CURRENT PRICE</div>
          <div class="expanded-stat-value">$${pred.lastClose.toFixed(2)}</div>
        </div>
        <div class="expanded-stat">
          <div class="expanded-stat-label">PREDICTED PRICE</div>
          <div class="expanded-stat-value">$${pred.predictedPrice.toFixed(2)}</div>
          <div class="change-indicator ${isPositive ? 'positive' : 'negative'}">
            ${isPositive ? '+' : ''}$${Math.abs(change).toFixed(2)} (${isPositive ? '+' : ''}${changePercent}%)
          </div>
        </div>
      </div>
      
      <div class="expanded-stats">
        <div class="expanded-stat">
          <div class="expanded-stat-label">METHOD</div>
          <div class="expanded-stat-value" style="font-size: 16px; text-transform: uppercase;">${pred.method || 'ema_drift'}</div>
        </div>
        <div class="expanded-stat">
          <div class="expanded-stat-label">CREATED</div>
          <div class="expanded-stat-value" style="font-size: 14px;">${new Date(pred.timestamp).toLocaleDateString()}</div>
        </div>
      </div>
      
      ${pred.feedback ? renderFeedbackResult(pred.feedback) : renderFeedbackButtons(index)}
      
      <button class="delete-btn" onclick="deletePrediction(${index})" style="width: 48px; height: 48px; margin: 16px auto 0; padding: 0; font-size: 16px; display: flex; align-items: center; justify-content: center;" title="Delete Prediction">
        <i class="fas fa-trash"></i>
      </button>
    </div>
  `;
  
  overlay.innerHTML = expandedHTML;
  overlay.classList.add('show');
  
  // Add smooth animation
  const expandedCard = overlay.querySelector('.expanded-card');
  if (expandedCard) {
    expandedCard.style.animation = 'fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
  }
  
  // Prevent body scrolling
  document.body.style.overflow = 'hidden';
}

// Render feedback buttons
function renderFeedbackButtons(index) {
  return `
    <div class="feedback-section" style="animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);">
      <div class="feedback-title">Was this prediction accurate?</div>
      <div class="feedback-btns">
        <button class="feedback-btn yes" onclick="handleFeedback(${index}, 'accurate')" style="animation: fadeInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) 0.1s backwards;">
          <i class="fas fa-check"></i> YES, ACCURATE
        </button>
        <button class="feedback-btn no" onclick="promptInaccuracy(${index})" style="animation: fadeInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) 0.2s backwards;">
          <i class="fas fa-times"></i> NO, INACCURATE
        </button>
      </div>
    </div>
  `;
}

// Render feedback result
function renderFeedbackResult(feedback) {
  if (feedback === 'accurate') {
    return `
      <div class="feedback-section">
        <div style="text-align: center; padding: 20px; background: var(--head-glass, rgba(72,182,255,0.15)); border-radius: 12px; border: 1px solid rgba(72,182,255,0.3);">
          <i class="fas fa-check-circle" style="font-size: 32px; color: #4ade80; margin-bottom: 8px;"></i>
          <div style="font-size: 14px; font-weight: 700; color: var(--ink, #fff); opacity: 0.9;">Marked as Accurate</div>
        </div>
      </div>
    `;
  } else {
    return `
      <div class="feedback-section">
        <div style="text-align: center; padding: 20px; background: var(--glass-bg, rgba(255,255,255,0.05)); border-radius: 12px; border: 1px solid var(--glass-border, rgba(255,255,255,0.2));">
          <i class="fas fa-times-circle" style="font-size: 32px; color: #f87171; margin-bottom: 8px;"></i>
          <div style="font-size: 14px; font-weight: 700; color: var(--ink, #fff); opacity: 0.7;">Marked as Inaccurate</div>
        </div>
      </div>
    `;
  }
}

// Handle accurate feedback
function handleFeedback(index, feedback) {
  // Submit feedback and close immediately
  submitFeedback(index, feedback, null);
  
  // Close expansion immediately
  const overlay = document.getElementById('expansionOverlay');
  overlay.classList.remove('show');
  overlay.innerHTML = '';
  document.body.style.overflow = '';
  
  // Show thank you modal
  showFeedbackModal('Thank you for verifying our model!', 'Your feedback helps us improve prediction accuracy.');
}

// Prompt for inaccuracy details
function promptInaccuracy(index) {
  const pred = currentPredictions[index];
  const overlay = document.getElementById('expansionOverlay');
  
  // Replace feedback section with inaccuracy input
  const feedbackSection = overlay.querySelector('.feedback-section');
  feedbackSection.style.animation = 'fadeOut 0.3s cubic-bezier(0.4, 0, 1, 1) forwards';
  
  setTimeout(() => {
    feedbackSection.innerHTML = `
      <div class="feedback-title" style="animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);">How inaccurate was it?</div>
      <div class="inaccuracy-section" style="animation: fadeInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) 0.1s backwards;">
        <label>Actual Price (optional)</label>
        <input type="number" step="0.01" id="actualPrice" placeholder="Enter actual price" />
        <button class="submit-feedback-btn" onclick="submitInaccuracy(${index})">
          SUBMIT FEEDBACK
        </button>
      </div>
      <button class="feedback-btn no" onclick="expandPrediction(${index})" style="margin-top: 12px; animation: fadeInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) 0.2s backwards;">
        <i class="fas fa-arrow-left"></i> BACK
      </button>
    `;
    feedbackSection.style.animation = 'fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
  }, 300);
}

// Submit inaccuracy feedback
function submitInaccuracy(index) {
  const actualPrice = document.getElementById('actualPrice').value;
  
  // Submit feedback and close immediately
  submitFeedback(index, 'inaccurate', actualPrice ? parseFloat(actualPrice) : null);
  
  // Close expansion immediately
  const overlay = document.getElementById('expansionOverlay');
  overlay.classList.remove('show');
  overlay.innerHTML = '';
  document.body.style.overflow = '';
  
  // Show thank you modal
  showFeedbackModal('Thank you for strengthening our model!', 'Your feedback helps us improve future predictions.');
}

// Submit feedback to backend
function submitFeedback(index, feedback, actualPrice = null) {
  const pred = currentPredictions[index];
  if (!pred) return;

  // Update local state immediately
  currentPredictions[index].feedback = feedback;
  if (actualPrice) {
    currentPredictions[index].actualPrice = actualPrice;
  }
  
  // Update localStorage for guest users
  const userEmail = localStorage.getItem('twin_user_email') || 'guest';
  if (userEmail === 'guest') {
    localStorage.setItem('twin_predictions', JSON.stringify(currentPredictions));
  }
  
  // Display updated predictions immediately
  displayPredictions();

  // Save to backend in background
  const token = localStorage.getItem('twin_supabase_token');
  if (token) {
    fetch('/save_feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        prediction_id: pred.id,
        feedback: feedback,
        actual_price: actualPrice
      })
    }).then(response => {
      if (response.ok) {
        console.log('Feedback saved to backend');
      }
    }).catch(error => {
      console.error('Error saving feedback:', error);
    });
  }
}

// Show feedback modal
function showFeedbackModal(title, message) {
  const overlay = document.getElementById('feedbackModalOverlay');
  const titleEl = document.getElementById('feedbackModalTitle');
  const messageEl = document.getElementById('feedbackModalMessage');
  
  titleEl.textContent = title;
  messageEl.textContent = message;
  
  // Add smooth entry animation
  requestAnimationFrame(() => {
    overlay.classList.add('show');
  });
}

// Close expansion
function closeExpansion() {
  const overlay = document.getElementById('expansionOverlay');
  const expandedCard = overlay.querySelector('.expanded-card');
  
  // Animate out before removing
  if (expandedCard) {
    expandedCard.style.animation = 'fadeOut 0.3s cubic-bezier(0.4, 0, 1, 1) forwards';
  }
  
  setTimeout(() => {
    overlay.classList.remove('show');
    overlay.innerHTML = '';
    document.body.style.overflow = '';
  }, 300);
}

// Delete prediction
function deletePrediction(index) {
  const pred = currentPredictions[index];
  if (!pred) return;

  // Immediately update data and UI
  currentPredictions.splice(index, 1);
  
  // Update localStorage for guest users
  const userEmail = localStorage.getItem('twin_user_email') || 'guest';
  if (userEmail === 'guest') {
    localStorage.setItem('twin_predictions', JSON.stringify(currentPredictions));
  }
  
  // Close expansion immediately without animation
  const overlay = document.getElementById('expansionOverlay');
  overlay.classList.remove('show');
  overlay.innerHTML = '';
  document.body.style.overflow = '';
  
  // Display updated predictions (no fetch)
  displayPredictions();
  
  // Delete from backend in background
  const token = localStorage.getItem('twin_supabase_token');
  if (token) {
    fetch(`/api/predictions/delete/${pred.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }).then(response => {
      if (response.ok) {
        console.log('Prediction deleted from backend');
      }
    }).catch(error => {
      console.error('Error deleting prediction:', error);
    });
  }
}

// Clear all predictions
function clearAllPredictions() {
  const modal = document.getElementById('clearAllModalOverlay');
  modal.classList.add('show');
}

// Confirm clear all
function confirmClearAll() {
  const token = localStorage.getItem('twin_supabase_token');
  
  // Immediately close modal and clear UI
  cancelClearAll();
  currentPredictions = [];
  displayPredictions();
  
  // Clear localStorage immediately
  localStorage.removeItem('twin_predictions');
  
  // Delete from backend in background
  if (token) {
    fetch('/api/predictions/clear', {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }).then(response => {
      if (response.ok) {
        console.log('All predictions cleared from backend');
      }
    }).catch(error => {
      console.error('Error clearing predictions:', error);
    });
  }
}

// Cancel clear all
function cancelClearAll() {
  const modal = document.getElementById('clearAllModalOverlay');
  modal.classList.remove('show');
}

// Close feedback modal
function closeFeedbackModal() {
  const overlay = document.getElementById('feedbackModalOverlay');
  const modal = overlay.querySelector('.feedback-modal');
  
  // Animate out
  modal.style.transform = 'scale(0.8) translateY(20px)';
  modal.style.opacity = '0';
  overlay.style.opacity = '0';
  
  setTimeout(() => {
    overlay.classList.remove('show');
  }, 400);
}

// Logout function
function logout() {
  // Clear all auth data
  localStorage.removeItem('twin_supabase_token');
  localStorage.removeItem('twin_user_email');
  localStorage.removeItem('twin_predictions');
  
  // Redirect to intro page
  window.location.href = 'intro.html';
}

// Setup event listeners
function setupEventListeners() {
  document.getElementById('logoutBtn').addEventListener('click', logout);
  document.getElementById('clearAllBtn').addEventListener('click', clearAllPredictions);
  document.getElementById('confirmClearAllBtn').addEventListener('click', confirmClearAll);
  document.getElementById('cancelClearAllBtn').addEventListener('click', cancelClearAll);
  document.getElementById('closeFeedbackModalBtn').addEventListener('click', closeFeedbackModal);
  
  // Close expansion when clicking overlay background
  document.getElementById('expansionOverlay').addEventListener('click', function(e) {
    if (e.target.id === 'expansionOverlay') {
      closeExpansion();
    }
  });
  
  // Close modals when clicking overlay background
  document.getElementById('feedbackModalOverlay').addEventListener('click', function(e) {
    if (e.target.id === 'feedbackModalOverlay') {
      closeFeedbackModal();
    }
  });
  
  document.getElementById('clearAllModalOverlay').addEventListener('click', function(e) {
    if (e.target.id === 'clearAllModalOverlay') {
      cancelClearAll();
    }
  });
}

// Make functions globally accessible for inline onclick handlers
window.deletePrediction = deletePrediction;
window.handleFeedback = handleFeedback;
window.promptInaccuracy = promptInaccuracy;
window.submitInaccuracy = submitInaccuracy;
window.expandPrediction = expandPrediction;
window.closeFeedbackModal = closeFeedbackModal;
window.closeExpansion = closeExpansion;
window.cancelClearAll = cancelClearAll;
window.confirmClearAll = confirmClearAll;

// Initialize
setupEventListeners();
