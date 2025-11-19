/**
 * Settings Panel Component
 *
 * Slide-out settings panel for API key management and configuration.
 */

import apiKeyManager from './api-key-manager.js';

class SettingsPanel {
  constructor(options = {}) {
    this.containerId = options.containerId || 'settingsPanel';
    this.onSave = options.onSave || null;
    this.isOpen = false;
  }

  /**
   * Initialize the settings panel
   */
  initialize() {
    this.render();
    this.attachEventListeners();
  }

  /**
   * Render the settings panel HTML
   */
  render() {
    // Create the panel if it doesn't exist
    let panel = document.getElementById(this.containerId);
    if (!panel) {
      panel = document.createElement('div');
      panel.id = this.containerId;
      document.body.appendChild(panel);
    }

    const html = `
      <!-- Backdrop -->
      <div id="settingsBackdrop" class="hidden fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"></div>

      <!-- Panel -->
      <div id="settingsPanelSlide" class="fixed top-0 right-0 h-full w-96 max-w-full bg-white shadow-2xl z-50 transform translate-x-full transition-transform duration-300 ease-in-out overflow-hidden flex flex-col" style="background-color: #121212;">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b" style="border-color: #262626;">
          <div class="flex items-center gap-3">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <h2 class="text-lg font-semibold" style="color: #e5e5e5;">Settings</h2>
          </div>
          <button id="closeSettingsBtn" class="p-1 rounded hover:bg-gray-800 transition-colors">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <!-- API Keys Section -->
          <div class="mb-6">
            <h3 class="text-sm font-semibold uppercase tracking-wide mb-4" style="color: #a3a3a3;">API Keys</h3>

            <!-- OpenRouter -->
            <div class="mb-4">
              <label class="block text-sm font-medium mb-2" style="color: #e5e5e5;">
                OpenRouter API Key
                <span class="text-xs font-normal ml-1" style="color: #737373;">(Recommended)</span>
              </label>
              <div class="relative">
                <input
                  type="password"
                  id="openrouterKeyInput"
                  placeholder="sk-or-..."
                  class="w-full rounded-lg border px-3 py-2 text-sm pr-10"
                  style="background-color: #1a1a1a; border-color: #333333; color: #e5e5e5;"
                />
                <button id="toggleOpenrouterKey" class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-gray-300">
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
              </div>
              <p class="mt-1 text-xs" style="color: #737373;">
                Get key at <a href="https://openrouter.ai/keys" target="_blank" class="text-blue-400 hover:underline">openrouter.ai/keys</a> • Access 300+ models
              </p>
            </div>

            <!-- OpenAI -->
            <div class="mb-4">
              <label class="block text-sm font-medium mb-2" style="color: #e5e5e5;">
                OpenAI API Key
                <span class="text-xs font-normal ml-1" style="color: #737373;">(ChatGPT Direct)</span>
              </label>
              <div class="relative">
                <input
                  type="password"
                  id="openaiKeyInput"
                  placeholder="sk-..."
                  class="w-full rounded-lg border px-3 py-2 text-sm pr-10"
                  style="background-color: #1a1a1a; border-color: #333333; color: #e5e5e5;"
                />
                <button id="toggleOpenaiKey" class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-gray-300">
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
              </div>
              <p class="mt-1 text-xs" style="color: #737373;">
                Get key at <a href="https://platform.openai.com/api-keys" target="_blank" class="text-blue-400 hover:underline">platform.openai.com</a>
              </p>
            </div>

            <!-- Anthropic -->
            <div class="mb-4">
              <label class="block text-sm font-medium mb-2" style="color: #e5e5e5;">
                Anthropic API Key
                <span class="text-xs font-normal ml-1" style="color: #737373;">(Claude Direct)</span>
              </label>
              <div class="relative">
                <input
                  type="password"
                  id="anthropicKeyInput"
                  placeholder="sk-ant-..."
                  class="w-full rounded-lg border px-3 py-2 text-sm pr-10"
                  style="background-color: #1a1a1a; border-color: #333333; color: #e5e5e5;"
                />
                <button id="toggleAnthropicKey" class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-gray-300">
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
              </div>
              <p class="mt-1 text-xs" style="color: #737373;">
                Get key at <a href="https://console.anthropic.com/settings/keys" target="_blank" class="text-blue-400 hover:underline">console.anthropic.com</a>
              </p>
            </div>
          </div>

          <!-- Default Provider Section -->
          <div class="mb-6">
            <h3 class="text-sm font-semibold uppercase tracking-wide mb-4" style="color: #a3a3a3;">Default Online Provider</h3>
            <select id="defaultProviderSelect" class="w-full rounded-lg border px-3 py-2 text-sm" style="background-color: #1a1a1a; border-color: #333333; color: #e5e5e5;">
              <option value="openrouter">OpenRouter (300+ models)</option>
              <option value="openai">OpenAI (ChatGPT)</option>
              <option value="anthropic">Anthropic (Claude)</option>
            </select>
            <p class="mt-1 text-xs" style="color: #737373;">
              Used when switching to Online mode
            </p>
          </div>

          <!-- Status Section -->
          <div class="mb-6">
            <h3 class="text-sm font-semibold uppercase tracking-wide mb-4" style="color: #a3a3a3;">Configuration Status</h3>
            <div id="configStatus" class="space-y-2">
              <!-- Populated dynamically -->
            </div>
          </div>

          <!-- Info Section -->
          <div class="rounded-lg p-4" style="background-color: #1a1a1a; border: 1px solid #333333;">
            <div class="flex items-start gap-3">
              <svg class="h-5 w-5 text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="text-xs" style="color: #a3a3a3;">
                <p class="font-medium mb-1" style="color: #e5e5e5;">Security Note</p>
                <p>API keys are stored locally in your browser and are never sent to our servers. They are only used to make direct API calls to the respective providers.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t" style="border-color: #262626;">
          <div class="flex gap-3">
            <button id="clearKeysBtn" class="flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition-colors" style="border-color: #333333; color: #e5e5e5; background-color: transparent;" onmouseover="this.style.backgroundColor='#1f1f1f'" onmouseout="this.style.backgroundColor='transparent'">
              Clear All
            </button>
            <button id="saveSettingsBtn" class="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors">
              Save Settings
            </button>
          </div>
        </div>
      </div>
    `;

    panel.innerHTML = html;
    this.loadCurrentValues();
    this.updateConfigStatus();
  }

  /**
   * Load current API key values into inputs
   */
  loadCurrentValues() {
    const openrouterKey = apiKeyManager.getKey('openrouter');
    const openaiKey = apiKeyManager.getKey('openai');
    const anthropicKey = apiKeyManager.getKey('anthropic');

    if (openrouterKey) {
      document.getElementById('openrouterKeyInput').value = openrouterKey;
    }
    if (openaiKey) {
      document.getElementById('openaiKeyInput').value = openaiKey;
    }
    if (anthropicKey) {
      document.getElementById('anthropicKeyInput').value = anthropicKey;
    }

    // Load default provider
    const defaultProvider = apiKeyManager.getDefaultProvider();
    document.getElementById('defaultProviderSelect').value = defaultProvider;
  }

  /**
   * Update configuration status indicators
   */
  updateConfigStatus() {
    const statusContainer = document.getElementById('configStatus');
    if (!statusContainer) return;

    const providers = [
      { id: 'openrouter', name: 'OpenRouter', icon: '🌐' },
      { id: 'openai', name: 'OpenAI', icon: '🤖' },
      { id: 'anthropic', name: 'Anthropic', icon: '🧠' }
    ];

    statusContainer.innerHTML = providers.map(provider => {
      const hasKey = apiKeyManager.hasKey(provider.id);
      const statusColor = hasKey ? 'bg-green-500' : 'bg-gray-600';
      const statusText = hasKey ? 'Configured' : 'Not configured';

      return `
        <div class="flex items-center justify-between py-2">
          <div class="flex items-center gap-2">
            <span>${provider.icon}</span>
            <span class="text-sm" style="color: #e5e5e5;">${provider.name}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="h-2 w-2 rounded-full ${statusColor}"></span>
            <span class="text-xs" style="color: ${hasKey ? '#10b981' : '#737373'};">${statusText}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  /**
   * Attach event listeners
   */
  attachEventListeners() {
    // Close button
    document.getElementById('closeSettingsBtn')?.addEventListener('click', () => this.close());

    // Backdrop click
    document.getElementById('settingsBackdrop')?.addEventListener('click', () => this.close());

    // Save button
    document.getElementById('saveSettingsBtn')?.addEventListener('click', () => this.save());

    // Clear button
    document.getElementById('clearKeysBtn')?.addEventListener('click', () => this.clearAll());

    // Toggle password visibility
    this.setupPasswordToggle('toggleOpenrouterKey', 'openrouterKeyInput');
    this.setupPasswordToggle('toggleOpenaiKey', 'openaiKeyInput');
    this.setupPasswordToggle('toggleAnthropicKey', 'anthropicKeyInput');

    // ESC key to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });
  }

  /**
   * Setup password toggle for an input
   */
  setupPasswordToggle(buttonId, inputId) {
    const button = document.getElementById(buttonId);
    const input = document.getElementById(inputId);

    if (button && input) {
      button.addEventListener('click', () => {
        input.type = input.type === 'password' ? 'text' : 'password';
      });
    }
  }

  /**
   * Open the settings panel
   */
  open() {
    const backdrop = document.getElementById('settingsBackdrop');
    const panel = document.getElementById('settingsPanelSlide');

    if (backdrop && panel) {
      backdrop.classList.remove('hidden');
      panel.classList.remove('translate-x-full');
      this.isOpen = true;
      this.loadCurrentValues();
      this.updateConfigStatus();
    }
  }

  /**
   * Close the settings panel
   */
  close() {
    const backdrop = document.getElementById('settingsBackdrop');
    const panel = document.getElementById('settingsPanelSlide');

    if (backdrop && panel) {
      backdrop.classList.add('hidden');
      panel.classList.add('translate-x-full');
      this.isOpen = false;
    }
  }

  /**
   * Save settings
   */
  save() {
    const openrouterKey = document.getElementById('openrouterKeyInput')?.value.trim();
    const openaiKey = document.getElementById('openaiKeyInput')?.value.trim();
    const anthropicKey = document.getElementById('anthropicKeyInput')?.value.trim();
    const defaultProvider = document.getElementById('defaultProviderSelect')?.value;

    // Save keys
    if (openrouterKey) {
      apiKeyManager.setKey('openrouter', openrouterKey);
    } else {
      apiKeyManager.removeKey('openrouter');
    }

    if (openaiKey) {
      apiKeyManager.setKey('openai', openaiKey);
    } else {
      apiKeyManager.removeKey('openai');
    }

    if (anthropicKey) {
      apiKeyManager.setKey('anthropic', anthropicKey);
    } else {
      apiKeyManager.removeKey('anthropic');
    }

    // Save default provider
    apiKeyManager.setDefaultProvider(defaultProvider);

    // Update status
    this.updateConfigStatus();

    // Notify callback
    if (this.onSave) {
      this.onSave({
        openrouter: !!openrouterKey,
        openai: !!openaiKey,
        anthropic: !!anthropicKey,
        defaultProvider
      });
    }

    // Show success message
    if (typeof window.toast === 'function') {
      window.toast('Settings saved successfully', 'success');
    }

    this.close();
  }

  /**
   * Clear all API keys
   */
  clearAll() {
    if (confirm('Are you sure you want to clear all API keys?')) {
      apiKeyManager.clearAll();

      // Clear inputs
      document.getElementById('openrouterKeyInput').value = '';
      document.getElementById('openaiKeyInput').value = '';
      document.getElementById('anthropicKeyInput').value = '';

      this.updateConfigStatus();

      if (typeof window.toast === 'function') {
        window.toast('All API keys cleared', 'info');
      }
    }
  }

  /**
   * Toggle panel open/close
   */
  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }
}

// Export singleton instance
const settingsPanel = new SettingsPanel();
export default settingsPanel;

// Also export class
export { SettingsPanel };
