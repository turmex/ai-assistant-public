/**
 * Online LLM Client
 *
 * Client for online LLM providers: OpenRouter, OpenAI (ChatGPT), and Anthropic (Claude).
 * Provides a unified interface for chat completions across providers.
 */

import apiKeyManager from './api-key-manager.js';

class OnlineLLMClient {
  constructor() {
    this.currentProvider = 'openrouter';
    this.currentModel = null;
    this.isGenerating = false;
  }

  /**
   * Set the current provider
   */
  setProvider(provider) {
    this.currentProvider = provider;
    console.log(`Online LLM provider set to: ${provider}`);
  }

  /**
   * Get available models for current provider
   */
  getAvailableModels() {
    switch (this.currentProvider) {
      case 'openrouter':
        return this.getOpenRouterModels();
      case 'openai':
        return this.getOpenAIModels();
      case 'anthropic':
        return this.getAnthropicModels();
      default:
        return [];
    }
  }

  /**
   * OpenRouter models (access to 300+ models)
   */
  getOpenRouterModels() {
    return [
      {
        name: 'openai/gpt-4o-mini',
        display_name: 'GPT-4o Mini',
        provider: 'OpenAI via OpenRouter',
        size_gb: 0,
        expected_performance: 'fastest',
        speed_estimate: '50-100 tokens/sec',
        quality: 'high',
        recommended: true,
        source: 'openrouter',
        description: 'Fast and affordable GPT-4 class model'
      },
      {
        name: 'openai/gpt-4o',
        display_name: 'GPT-4o',
        provider: 'OpenAI via OpenRouter',
        size_gb: 0,
        expected_performance: 'fast',
        speed_estimate: '30-60 tokens/sec',
        quality: 'excellent',
        recommended: false,
        source: 'openrouter',
        description: 'Most capable GPT-4 model'
      },
      {
        name: 'anthropic/claude-3.5-sonnet',
        display_name: 'Claude 3.5 Sonnet',
        provider: 'Anthropic via OpenRouter',
        size_gb: 0,
        expected_performance: 'fast',
        speed_estimate: '40-80 tokens/sec',
        quality: 'excellent',
        recommended: false,
        source: 'openrouter',
        description: 'Best balance of speed and intelligence'
      },
      {
        name: 'anthropic/claude-3-haiku',
        display_name: 'Claude 3 Haiku',
        provider: 'Anthropic via OpenRouter',
        size_gb: 0,
        expected_performance: 'fastest',
        speed_estimate: '80-150 tokens/sec',
        quality: 'high',
        recommended: false,
        source: 'openrouter',
        description: 'Fastest Claude model'
      },
      {
        name: 'meta-llama/llama-3.2-90b-vision-instruct',
        display_name: 'Llama 3.2 90B',
        provider: 'Meta via OpenRouter',
        size_gb: 0,
        expected_performance: 'good',
        speed_estimate: '20-40 tokens/sec',
        quality: 'excellent',
        recommended: false,
        source: 'openrouter',
        description: 'Largest open-source Llama model'
      },
      {
        name: 'google/gemini-pro-1.5',
        display_name: 'Gemini Pro 1.5',
        provider: 'Google via OpenRouter',
        size_gb: 0,
        expected_performance: 'fast',
        speed_estimate: '40-80 tokens/sec',
        quality: 'excellent',
        recommended: false,
        source: 'openrouter',
        description: 'Google\'s most capable model'
      },
      {
        name: 'mistralai/mistral-large',
        display_name: 'Mistral Large',
        provider: 'Mistral via OpenRouter',
        size_gb: 0,
        expected_performance: 'fast',
        speed_estimate: '30-60 tokens/sec',
        quality: 'excellent',
        recommended: false,
        source: 'openrouter',
        description: 'Top-tier Mistral model'
      },
      {
        name: 'qwen/qwen-2.5-72b-instruct',
        display_name: 'Qwen 2.5 72B',
        provider: 'Alibaba via OpenRouter',
        size_gb: 0,
        expected_performance: 'good',
        speed_estimate: '25-50 tokens/sec',
        quality: 'excellent',
        recommended: false,
        source: 'openrouter',
        description: 'Alibaba\'s flagship model'
      }
    ];
  }

  /**
   * OpenAI direct API models
   */
  getOpenAIModels() {
    return [
      {
        name: 'gpt-4o-mini',
        display_name: 'GPT-4o Mini',
        provider: 'OpenAI Direct',
        size_gb: 0,
        expected_performance: 'fastest',
        speed_estimate: '50-100 tokens/sec',
        quality: 'high',
        recommended: true,
        source: 'openai',
        description: 'Fast and affordable'
      },
      {
        name: 'gpt-4o',
        display_name: 'GPT-4o',
        provider: 'OpenAI Direct',
        size_gb: 0,
        expected_performance: 'fast',
        speed_estimate: '30-60 tokens/sec',
        quality: 'excellent',
        recommended: false,
        source: 'openai',
        description: 'Most capable GPT-4'
      },
      {
        name: 'gpt-4-turbo',
        display_name: 'GPT-4 Turbo',
        provider: 'OpenAI Direct',
        size_gb: 0,
        expected_performance: 'fast',
        speed_estimate: '30-50 tokens/sec',
        quality: 'excellent',
        recommended: false,
        source: 'openai',
        description: '128K context window'
      },
      {
        name: 'gpt-3.5-turbo',
        display_name: 'GPT-3.5 Turbo',
        provider: 'OpenAI Direct',
        size_gb: 0,
        expected_performance: 'fastest',
        speed_estimate: '80-120 tokens/sec',
        quality: 'good',
        recommended: false,
        source: 'openai',
        description: 'Fast and cheap'
      }
    ];
  }

  /**
   * Anthropic direct API models
   */
  getAnthropicModels() {
    return [
      {
        name: 'claude-3-5-sonnet-20241022',
        display_name: 'Claude 3.5 Sonnet',
        provider: 'Anthropic Direct',
        size_gb: 0,
        expected_performance: 'fast',
        speed_estimate: '40-80 tokens/sec',
        quality: 'excellent',
        recommended: true,
        source: 'anthropic',
        description: 'Best balance of speed and intelligence'
      },
      {
        name: 'claude-3-5-haiku-20241022',
        display_name: 'Claude 3.5 Haiku',
        provider: 'Anthropic Direct',
        size_gb: 0,
        expected_performance: 'fastest',
        speed_estimate: '80-150 tokens/sec',
        quality: 'high',
        recommended: false,
        source: 'anthropic',
        description: 'Fastest Claude model'
      },
      {
        name: 'claude-3-opus-20240229',
        display_name: 'Claude 3 Opus',
        provider: 'Anthropic Direct',
        size_gb: 0,
        expected_performance: 'good',
        speed_estimate: '20-40 tokens/sec',
        quality: 'excellent',
        recommended: false,
        source: 'anthropic',
        description: 'Most capable Claude'
      }
    ];
  }

  /**
   * Main chat function
   */
  async chat(messages, options = {}) {
    if (this.isGenerating) {
      throw new Error('Generation already in progress');
    }

    const apiKey = apiKeyManager.getKey(this.currentProvider);
    if (!apiKey) {
      throw new Error(`No API key configured for ${this.currentProvider}. Please add your key in Settings.`);
    }

    this.isGenerating = true;

    try {
      let response;
      switch (this.currentProvider) {
        case 'openrouter':
          response = await this.chatOpenRouter(messages, options, apiKey);
          break;
        case 'openai':
          response = await this.chatOpenAI(messages, options, apiKey);
          break;
        case 'anthropic':
          response = await this.chatAnthropic(messages, options, apiKey);
          break;
        default:
          throw new Error(`Unknown provider: ${this.currentProvider}`);
      }

      this.isGenerating = false;
      return response;
    } catch (error) {
      this.isGenerating = false;
      throw error;
    }
  }

  /**
   * OpenRouter API
   */
  async chatOpenRouter(messages, options, apiKey) {
    const model = options.model || 'openai/gpt-4o-mini';

    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': window.location.origin,
        'X-Title': 'AI Assistant'
      },
      body: JSON.stringify({
        model: model,
        messages: messages,
        temperature: options.temperature || 0.7,
        max_tokens: options.max_tokens || 1024,
        stream: false
      })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error?.message || `OpenRouter API error: ${response.status}`);
    }

    const data = await response.json();
    return {
      content: data.choices[0].message.content,
      model: model,
      usage: data.usage
    };
  }

  /**
   * OpenAI API
   */
  async chatOpenAI(messages, options, apiKey) {
    const model = options.model || 'gpt-4o-mini';

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: model,
        messages: messages,
        temperature: options.temperature || 0.7,
        max_tokens: options.max_tokens || 1024
      })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error?.message || `OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    return {
      content: data.choices[0].message.content,
      model: model,
      usage: data.usage
    };
  }

  /**
   * Anthropic API
   */
  async chatAnthropic(messages, options, apiKey) {
    const model = options.model || 'claude-3-5-sonnet-20241022';

    // Convert messages format for Anthropic
    const systemMessage = messages.find(m => m.role === 'system');
    const chatMessages = messages.filter(m => m.role !== 'system');

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true'
      },
      body: JSON.stringify({
        model: model,
        max_tokens: options.max_tokens || 1024,
        system: systemMessage?.content || '',
        messages: chatMessages.map(m => ({
          role: m.role,
          content: m.content
        }))
      })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error?.message || `Anthropic API error: ${response.status}`);
    }

    const data = await response.json();
    return {
      content: data.content[0].text,
      model: model,
      usage: {
        prompt_tokens: data.usage?.input_tokens,
        completion_tokens: data.usage?.output_tokens
      }
    };
  }

  /**
   * Set current model
   */
  setModel(model) {
    this.currentModel = model;
  }

  /**
   * Get current model
   */
  getCurrentModel() {
    return this.currentModel;
  }

  /**
   * Check if provider is configured
   */
  isConfigured() {
    return apiKeyManager.hasKey(this.currentProvider);
  }
}

// Export singleton instance
const onlineLLMClient = new OnlineLLMClient();
export default onlineLLMClient;

// Also export class
export { OnlineLLMClient };
