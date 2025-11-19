/**
 * API Key Manager
 *
 * Securely manages API keys for online LLM providers.
 * Keys are stored in localStorage with base64 obfuscation.
 */

class APIKeyManager {
  constructor() {
    this.storageKey = 'ai-assistant-api-keys';
    this.keys = this.loadKeys();
  }

  /**
   * Load keys from localStorage
   */
  loadKeys() {
    try {
      const encrypted = localStorage.getItem(this.storageKey);
      if (!encrypted) return {};
      // Simple obfuscation for localStorage
      return JSON.parse(atob(encrypted));
    } catch (error) {
      console.error('Failed to load API keys:', error);
      return {};
    }
  }

  /**
   * Save keys to localStorage
   */
  saveKeys(keys) {
    try {
      const encrypted = btoa(JSON.stringify(keys));
      localStorage.setItem(this.storageKey, encrypted);
      this.keys = keys;
      console.log('✓ API keys saved');
      return true;
    } catch (error) {
      console.error('Failed to save API keys:', error);
      return false;
    }
  }

  /**
   * Set a specific provider's API key
   */
  setKey(provider, key) {
    this.keys[provider] = key;
    return this.saveKeys(this.keys);
  }

  /**
   * Get a specific provider's API key
   */
  getKey(provider) {
    return this.keys[provider] || '';
  }

  /**
   * Check if a provider has a key configured
   */
  hasKey(provider) {
    return !!this.keys[provider] && this.keys[provider].trim() !== '';
  }

  /**
   * Remove a specific provider's API key
   */
  removeKey(provider) {
    delete this.keys[provider];
    return this.saveKeys(this.keys);
  }

  /**
   * Get all configured providers
   */
  getConfiguredProviders() {
    return Object.keys(this.keys).filter(key => this.hasKey(key));
  }

  /**
   * Mask key for display: sk-abc...xyz
   */
  maskKey(key) {
    if (!key || key.length < 10) return '••••••••';
    return `${key.slice(0, 7)}...${key.slice(-4)}`;
  }

  /**
   * Validate API key format
   */
  validateKey(provider, key) {
    if (!key || key.trim() === '') return { valid: false, error: 'Key is empty' };

    switch (provider) {
      case 'openrouter':
        if (!key.startsWith('sk-or-')) {
          return { valid: false, error: 'OpenRouter keys start with sk-or-' };
        }
        break;
      case 'openai':
        if (!key.startsWith('sk-')) {
          return { valid: false, error: 'OpenAI keys start with sk-' };
        }
        break;
      case 'anthropic':
        if (!key.startsWith('sk-ant-')) {
          return { valid: false, error: 'Anthropic keys start with sk-ant-' };
        }
        break;
    }

    return { valid: true };
  }

  /**
   * Get default online provider based on configured keys
   */
  getDefaultProvider() {
    const saved = localStorage.getItem('ai-assistant-default-online-provider');
    if (saved && this.hasKey(saved)) return saved;

    // Fallback priority: OpenRouter > OpenAI > Anthropic
    if (this.hasKey('openrouter')) return 'openrouter';
    if (this.hasKey('openai')) return 'openai';
    if (this.hasKey('anthropic')) return 'anthropic';

    return 'openrouter'; // Default even if not configured
  }

  /**
   * Set default online provider
   */
  setDefaultProvider(provider) {
    localStorage.setItem('ai-assistant-default-online-provider', provider);
  }

  /**
   * Clear all keys
   */
  clearAll() {
    this.keys = {};
    localStorage.removeItem(this.storageKey);
    console.log('✓ All API keys cleared');
  }
}

// Export singleton instance
const apiKeyManager = new APIKeyManager();
export default apiKeyManager;

// Also export class for manual instantiation
export { APIKeyManager };
