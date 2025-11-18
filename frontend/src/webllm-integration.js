/**
 * WebLLM Integration
 *
 * Client-side LLM inference using WebLLM (runs in browser via WebGPU).
 * Provides a unified interface for loading models and generating responses.
 */

import * as webllm from "https://esm.run/@mlc-ai/web-llm";

class WebLLMClient {
  constructor() {
    this.engine = null;
    this.currentModel = null;
    this.isInitialized = false;
    this.isGenerating = false;
    this.progressCallback = null;
  }

  /**
   * Initialize WebLLM engine
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    try {
      console.log("Initializing WebLLM engine...");

      // Check WebGPU support
      if (!navigator.gpu) {
        throw new Error("WebGPU is not supported in this browser");
      }

      this.engine = await webllm.CreateMLCEngine("Llama-3.2-1B-Instruct-q4f16_1-MLC", {
        initProgressCallback: (progress) => {
          console.log("WebLLM init progress:", progress);
          if (this.progressCallback) {
            this.progressCallback(progress);
          }
        }
      });

      this.currentModel = "Llama-3.2-1B-Instruct-q4f16_1-MLC";
      this.isInitialized = true;

      console.log("✓ WebLLM engine initialized successfully");
      return true;

    } catch (error) {
      console.error("Failed to initialize WebLLM:", error);
      this.isInitialized = false;
      return false;
    }
  }

  /**
   * Load a specific model
   * @param {string} modelId - Model ID to load
   * @returns {Promise<boolean>} Success status
   */
  async loadModel(modelId) {
    try {
      console.log(`Loading model: ${modelId}`);

      if (!this.isInitialized || !this.engine) {
        // Initialize with the specified model
        this.engine = await webllm.CreateMLCEngine(modelId, {
          initProgressCallback: (progress) => {
            console.log("Model load progress:", progress);
            if (this.progressCallback) {
              this.progressCallback(progress);
            }
          }
        });
      } else {
        // Reload with new model
        await this.engine.reload(modelId, {
          initProgressCallback: (progress) => {
            console.log("Model reload progress:", progress);
            if (this.progressCallback) {
              this.progressCallback(progress);
            }
          }
        });
      }

      this.currentModel = modelId;
      this.isInitialized = true;

      console.log(`✓ Model ${modelId} loaded successfully`);
      return true;

    } catch (error) {
      console.error(`Failed to load model ${modelId}:`, error);
      return false;
    }
  }

  /**
   * Generate a response from the model
   * @param {Array<{role: string, content: string}>} messages - Conversation history
   * @param {Object} options - Generation options
   * @returns {Promise<string>} Generated response
   */
  async chat(messages, options = {}) {
    if (!this.isInitialized || !this.engine) {
      throw new Error("WebLLM engine not initialized. Call initialize() first.");
    }

    if (this.isGenerating) {
      throw new Error("Generation already in progress");
    }

    try {
      this.isGenerating = true;

      const completion = await this.engine.chat.completions.create({
        messages: messages,
        temperature: options.temperature || 0.7,
        max_tokens: options.max_tokens || 512,
        stream: false, // Non-streaming for simplicity
      });

      const response = completion.choices[0].message.content;

      this.isGenerating = false;
      return response;

    } catch (error) {
      this.isGenerating = false;
      console.error("WebLLM chat failed:", error);
      throw error;
    }
  }

  /**
   * Generate a response with streaming
   * @param {Array<{role: string, content: string}>} messages - Conversation history
   * @param {Function} onChunk - Callback for each chunk
   * @param {Object} options - Generation options
   */
  async chatStream(messages, onChunk, options = {}) {
    if (!this.isInitialized || !this.engine) {
      throw new Error("WebLLM engine not initialized. Call initialize() first.");
    }

    if (this.isGenerating) {
      throw new Error("Generation already in progress");
    }

    try {
      this.isGenerating = true;

      const chunks = await this.engine.chat.completions.create({
        messages: messages,
        temperature: options.temperature || 0.7,
        max_tokens: options.max_tokens || 512,
        stream: true, // Enable streaming
      });

      let fullResponse = "";

      for await (const chunk of chunks) {
        const content = chunk.choices[0]?.delta?.content || "";
        if (content) {
          fullResponse += content;
          if (onChunk) {
            onChunk(content);
          }
        }
      }

      this.isGenerating = false;
      return fullResponse;

    } catch (error) {
      this.isGenerating = false;
      console.error("WebLLM streaming failed:", error);
      throw error;
    }
  }

  /**
   * Get available models (from backend catalog)
   * @returns {Promise<Array>} List of available models
   */
  async getAvailableModels() {
    try {
      const response = await fetch('http://localhost:8000/api/providers/webllm/models');
      const data = await response.json();
      return data.models || [];
    } catch (error) {
      console.error("Failed to fetch WebLLM models:", error);
      return [];
    }
  }

  /**
   * Get current model info
   * @returns {Object|null} Current model info
   */
  getCurrentModel() {
    return this.currentModel;
  }

  /**
   * Check if WebGPU is supported
   * @returns {boolean} WebGPU support status
   */
  static isWebGPUSupported() {
    return !!navigator.gpu;
  }

  /**
   * Set progress callback for model loading
   * @param {Function} callback - Progress callback function
   */
  setProgressCallback(callback) {
    this.progressCallback = callback;
  }

  /**
   * Cleanup and unload resources
   */
  async cleanup() {
    try {
      if (this.engine) {
        // WebLLM doesn't have explicit cleanup, but we can clear references
        this.engine = null;
        this.currentModel = null;
        this.isInitialized = false;
        console.log("✓ WebLLM resources cleaned up");
      }
    } catch (error) {
      console.error("Error during cleanup:", error);
    }
  }
}

// Export singleton instance
const webllmClient = new WebLLMClient();
export default webllmClient;

// Also export class for manual instantiation if needed
export { WebLLMClient };
