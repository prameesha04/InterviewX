/**
 * InterviewX — app.js
 * Shared utility functions used across all pages.
 */

// ================================================================
// TOAST NOTIFICATIONS
// ================================================================

function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ================================================================
// BUTTON LOADING STATE
// ================================================================

/**
 * Toggle a button's loading state.
 * @param {HTMLButtonElement} btn
 * @param {boolean} loading
 * @param {string} [loadingText] — optional text to show while loading
 */
function setLoading(btn, loading, loadingText = null) {
  if (!btn) return;
  const textEl = btn.querySelector('.btn-text');
  const loaderEl = btn.querySelector('.btn-loader');

  btn.disabled = loading;

  if (textEl && loaderEl) {
    textEl.classList.toggle('hidden', loading);
    loaderEl.classList.toggle('hidden', !loading);
    if (loading && loadingText) loaderEl.textContent = loadingText;
  } else if (loadingText && loading) {
    btn.dataset.originalText = btn.textContent;
    btn.textContent = loadingText;
  } else if (!loading && btn.dataset.originalText) {
    btn.textContent = btn.dataset.originalText;
  }
}

// ================================================================
// DOM READY
// ================================================================

document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss flash messages after 5 seconds
  document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => {
      flash.style.transition = 'opacity 0.5s';
      flash.style.opacity = '0';
      setTimeout(() => flash.remove(), 500);
    }, 5000);
  });
});
