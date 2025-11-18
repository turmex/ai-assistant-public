/**
 * Provider Toggle Component
 *
 * UI component for switching between LLM providers (Ollama vs WebLLM).
 * Manages provider selection and persists user preference.
 */

class ProviderToggle {
  constructor(options = {}) {
    this.currentProvider = options.defaultProvider || 'webllm';
    this.containerId = options.containerId || 'providerToggle';
    this.onProviderChange = options.onProviderChange || null;
    this.storageKey = 'ai-assistant-provider-preference';

    // Load saved preference
    this.loadPreference();
  }

  /**
   * Initialize the toggle component
   */
  initialize() {
    this.render();
    this.attachEventListeners();
  }

  /**
   * Render the toggle UI
   */
  render() {
    const container = document.getElementById(this.containerId);
    if (!container) {
      console.error(`Container #${this.containerId} not found`);
      return;
    }

    const html = `
      <div class="provider-toggle-wrapper">
        <div class="provider-toggle-container">
          <div class="provider-toggle-label">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="provider-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z" />
            </svg>
            <span class="provider-label-text">Provider:</span>
          </div>

          <div class="provider-options">
            <button
              class="provider-option ${this.currentProvider === 'webllm' ? 'active' : ''}"
              data-provider="webllm"
              title="Browser-based LLM using WebGPU (faster, no server needed)"
            >
              <svg class="provider-option-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
              <span class="provider-option-text">WebLLM</span>
              <span class="provider-badge">Browser</span>
            </button>

            <button
              class="provider-option ${this.currentProvider === 'ollama' ? 'active' : ''}"
              data-provider="ollama"
              title="Local Ollama server (more models, higher quality)"
            >
              <svg class="provider-option-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z" />
              </svg>
              <span class="provider-option-text">Ollama</span>
              <span class="provider-badge">Local</span>
            </button>
          </div>

          <div class="provider-info">
            <div class="provider-info-content" id="providerInfoContent">
              ${this.getProviderInfo(this.currentProvider)}
            </div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  /**
   * Get provider information text
   */
  getProviderInfo(provider) {
    const info = {
      webllm: {
        icon: '⚡',
        title: 'WebLLM (Browser)',
        description: 'Runs entirely in your browser using WebGPU. No server needed, instant responses.',
        features: ['No API required', 'Completely private', 'Fast inference', 'Works offline']
      },
      ollama: {
        icon: '🖥️',
        title: 'Ollama (Local Server)',
        description: 'Uses local Ollama server for more powerful models and better quality.',
        features: ['More models available', 'Higher quality', 'Larger context', 'Better for complex tasks']
      }
    };

    const providerInfo = info[provider];
    const features = providerInfo.features.map(f => `<li>${f}</li>`).join('');

    return `
      <div class="provider-info-header">
        <span class="provider-info-icon">${providerInfo.icon}</span>
        <strong>${providerInfo.title}</strong>
      </div>
      <p class="provider-info-description">${providerInfo.description}</p>
      <ul class="provider-info-features">${features}</ul>
    `;
  }

  /**
   * Attach event listeners
   */
  attachEventListeners() {
    const options = document.querySelectorAll('.provider-option');

    options.forEach(option => {
      option.addEventListener('click', async (e) => {
        const provider = option.dataset.provider;

        if (provider === this.currentProvider) {
          return; // Already selected
        }

        // Update UI
        options.forEach(opt => opt.classList.remove('active'));
        option.classList.add('active');

        // Update provider info
        const infoContent = document.getElementById('providerInfoContent');
        if (infoContent) {
          infoContent.innerHTML = this.getProviderInfo(provider);
        }

        // Switch provider
        await this.switchProvider(provider);
      });
    });
  }

  /**
   * Switch to a different provider
   */
  async switchProvider(provider) {
    console.log(`Switching to provider: ${provider}`);

    try {
      // Save preference
      this.currentProvider = provider;
      this.savePreference();

      // Notify callback
      if (this.onProviderChange) {
        await this.onProviderChange(provider);
      }

      // Show success toast
      this.showToast(`Switched to ${provider === 'webllm' ? 'WebLLM (Browser)' : 'Ollama (Local)'}`, 'success');

    } catch (error) {
      console.error('Failed to switch provider:', error);
      this.showToast('Failed to switch provider: ' + error.message, 'error');
    }
  }

  /**
   * Save provider preference to localStorage
   */
  savePreference() {
    try {
      localStorage.setItem(this.storageKey, this.currentProvider);
      console.log(`✓ Saved provider preference: ${this.currentProvider}`);
    } catch (error) {
      console.error('Failed to save provider preference:', error);
    }
  }

  /**
   * Load provider preference from localStorage
   */
  loadPreference() {
    try {
      const saved = localStorage.getItem(this.storageKey);
      if (saved) {
        this.currentProvider = saved;
        console.log(`✓ Loaded provider preference: ${this.currentProvider}`);
      }
    } catch (error) {
      console.error('Failed to load provider preference:', error);
    }
  }

  /**
   * Get current provider
   */
  getCurrentProvider() {
    return this.currentProvider;
  }

  /**
   * Show toast notification
   */
  showToast(message, type = 'info') {
    // Check if toast function exists (from main app)
    if (typeof window.toast === 'function') {
      window.toast(message, type);
    } else {
      console.log(`[${type.toUpperCase()}] ${message}`);
    }
  }
}

// Export for use in other modules
export default ProviderToggle;
