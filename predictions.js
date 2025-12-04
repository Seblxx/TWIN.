// Predictions.js - Complete rebuild
const THEMES = [
  { name: 'Royal', file: 'royal.css', color: 'linear-gradient(135deg, #1e3a8a, #3b82f6)' },
  { name: 'Dark', file: 'dark.css', color: '#1a1a2e' },
  { name: 'Light', file: 'light.css', color: '#f0f0f0' },
  { name: 'Monochrome', file: 'monochrome.css', color: '#1e3a5f' },
  { name: 'Liquid Glass', file: 'liquidglass.css', color: '#000000' }
];

let currentThemeIndex = 0;
let selectedPredictionId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  loadPredictions();
  setupEventListeners();
  console.log('Predictions page initialized');
  console.log('Saved predictions:', getPredictions());
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

// Save predictions to localStorage (for guest users only)
function savePredictions(predictions) {
  try {
    localStorage.setItem('twin_predictions', JSON.stringify(predictions));
  } catch (e) {
    console.error('Failed to save predictions:', e);
  }
}

// Load and display predictions
async function loadPredictions() {
  const predictions = await getPredictions();
  const list = document.getElementById('predictionsList');
  const countEl = document.getElementById('predictionsCount');
  
  console.log('Loading predictions...');
  console.log('Raw localStorage:', localStorage.getItem('twin_predictions'));
  console.log('Parsed predictions:', predictions);
  console.log('Number of predictions:', predictions.length);
  
  // Update count
  countEl.textContent = `${predictions.length} PREDICTION${predictions.length !== 1 ? 'S' : ''}`;
  
  if (predictions.length === 0) {
    list.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-chart-line"></i>
        <h3>No predictions yet</h3>
        <p>Save a prediction using the star icon on index.html</p>
      </div>
    `;
    return;
  }

  list.innerHTML = predictions.map((pred, index) => {
    console.log(`Rendering prediction ${index}:`, pred);
    const change = pred.predictedPrice - pred.lastClose;
    const changePercent = ((change / pred.lastClose) * 100).toFixed(2);
    const isPositive = change > 0;
    
    let feedbackHTML = '';
    if (pred.feedback) {
      if (pred.feedback === 'accurate') {
        feedbackHTML = '<div class="feedback-result accurate">✓ Marked accurate</div>';
      } else {
        feedbackHTML = '<div class="feedback-result inaccurate">✗ Marked inaccurate</div>';
      }
    } else {
      feedbackHTML = `
        <div class="feedback-btns">
          <button class="feedback-btn yes" onclick="submitFeedback(${index}, 'accurate')">
            <i class="fas fa-check"></i> Accurate
          </button>
          <button class="feedback-btn no" onclick="submitFeedback(${index}, 'inaccurate')">
            <i class="fas fa-times"></i> Inaccurate
          </button>
        </div>
      `;
    }
    
    return `
      <div class="prediction-item" data-index="${index}">
        <div class="item-header">
          <div class="item-left">
            <div class="stock-symbol">${pred.stock}</div>
            <div class="duration-badge">${pred.duration}</div>
          </div>
          <div class="item-right">
            <div class="timestamp">${formatDate(pred.timestamp)}</div>
            <div class="method-badge">${pred.method}</div>
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
          <div class="stat-item">
            <div class="stat-label">CHANGE</div>
            <div class="stat-value ${isPositive ? 'positive' : 'negative'}">
              ${isPositive ? '+' : ''}${change.toFixed(2)} (${isPositive ? '+' : ''}${changePercent}%)
            </div>
          </div>
        </div>
        
        <div class="item-details">
          <div class="feedback-section">
            <div class="feedback-title">WAS THIS ACCURATE?</div>
            ${feedbackHTML}
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Add click handlers to toggle expanded state
  document.querySelectorAll('.prediction-item').forEach(item => {
    item.addEventListener('click', () => {
      item.classList.toggle('expanded');
    });
  });
}

// Submit feedback
function submitFeedback(index, feedback) {
  const predictions = getPredictions();
  if (!predictions[index]) return;

  predictions[index].feedback = feedback;
  savePredictions(predictions);
  loadPredictions(); // Refresh display
}

// Format date
function formatDate(timestamp) {
  const date = new Date(timestamp);
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = date.getHours();
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const ampm = hours >= 12 ? 'p.m.' : 'a.m.';
  const displayHours = hours % 12 || 12;
  
  return `${date.getFullYear()}-${month}-${day} ${displayHours}:${minutes} ${ampm}`;
}

// Clear all predictions
function clearAllPredictions() {
  // Use the shared modal system from theme-toggle.js
  if (typeof window.showConfirmModal === 'function') {
    window.showConfirmModal(
      'Clear All Predictions?',
      'This will permanently delete all your saved predictions.',
      () => {
        const token = localStorage.getItem('twin_supabase_token');
        
        if (token) {
          // Delete from backend
          fetch('/api/predictions/clear', {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          .then(response => {
            if (!response.ok) {
              throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
          })
          .then(data => {
            if (data.success) {
              console.log('Predictions cleared from database');
              loadPredictions();
            } else {
              // Backend returned error, clear localStorage as fallback
              console.warn('Backend failed, clearing localStorage');
              localStorage.removeItem('twin_predictions');
              selectedPredictionId = null;
              loadPredictions();
            }
          })
          .catch(error => {
            console.error('Error clearing predictions:', error);
            // Fallback to localStorage
            localStorage.removeItem('twin_predictions');
            selectedPredictionId = null;
            loadPredictions();
          });
        } else {
          // Clear from localStorage only
          localStorage.removeItem('twin_predictions');
          selectedPredictionId = null;
          loadPredictions();
        }
      }
    );
  } else {
    // Fallback to confirm dialog
    if (confirm('Are you sure you want to clear all predictions?')) {
      localStorage.removeItem('twin_predictions');
      selectedPredictionId = null;
      loadPredictions();
    }
  }
}

// Setup event listeners
function setupEventListeners() {
  document.getElementById('themeToggle').addEventListener('click', cycleTheme);
  document.getElementById('clearAllBtn').addEventListener('click', clearAllPredictions);
}
