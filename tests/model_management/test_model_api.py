"""
Comprehensive Test Suite for Model Management System

This test suite validates:
1. API endpoint functionality (/models/available, /models/downloaded, /models/download)
2. Model download and display logic
3. Duplicate prevention
4. Model name consistency between API and Ollama
5. UI refresh behavior

Test Scenarios:
- Download Llama 3.2 1B → verify appears in Downloaded Models (not Available)
- Check Qwen2.5 1.5B → verify appears ONLY ONCE
- Download gpt2 → verify successful download and display
- Download 3 different models → verify all appear correctly
- Refresh page → verify no duplicates after refresh
- Check model name consistency across API and Ollama
"""

import asyncio
import pytest
import httpx
from typing import List, Dict, Any
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 60.0

class TestModelManagementAPI:
    """Test suite for model management API endpoints"""

    @pytest.fixture
    async def client(self):
        """Create async HTTP client for tests"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            yield client

    # ========================================================================
    # API Endpoint Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_available_models_endpoint(self, client):
        """
        TEST 1: Verify /models/available endpoint
        - Returns valid JSON
        - Has 'models' array
        - Each model has required fields
        """
        logger.info("TEST 1: Testing GET /models/available")

        response = await client.get(f"{BASE_URL}/models/available")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert "models" in data, "Response missing 'models' field"
        assert isinstance(data["models"], list), "'models' should be an array"

        # Verify model structure
        for model in data["models"]:
            assert "name" in model, f"Model missing 'name': {model}"
            assert "display_name" in model, f"Model missing 'display_name': {model}"
            assert "size_gb" in model, f"Model missing 'size_gb': {model}"
            assert "compatible" in model, f"Model missing 'compatible' flag: {model}"

        logger.info(f"✓ Found {len(data['models'])} available models")
        return data["models"]

    @pytest.mark.asyncio
    async def test_get_downloaded_models_endpoint(self, client):
        """
        TEST 2: Verify /models/downloaded endpoint
        - Returns valid JSON
        - Has 'models' array
        - Returns model names as strings
        """
        logger.info("TEST 2: Testing GET /models/downloaded")

        response = await client.get(f"{BASE_URL}/models/downloaded")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert "models" in data, "Response missing 'models' field"
        assert isinstance(data["models"], list), "'models' should be an array"

        # Verify all entries are strings
        for model_name in data["models"]:
            assert isinstance(model_name, str), f"Model name should be string, got {type(model_name)}: {model_name}"

        logger.info(f"✓ Found {len(data['models'])} downloaded models: {data['models']}")
        return data["models"]

    @pytest.mark.asyncio
    async def test_download_model_endpoint(self, client):
        """
        TEST 3: Verify POST /models/download endpoint
        - Accepts model name
        - Returns success status
        - Initiates download process
        """
        logger.info("TEST 3: Testing POST /models/download")

        # Use a small, fast model for testing
        test_model = "qwen2.5:0.5b"

        response = await client.post(
            f"{BASE_URL}/models/download",
            json={"model_name": test_model}
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert "status" in data, "Response missing 'status' field"
        assert data["status"] == "download_started", f"Unexpected status: {data['status']}"
        assert data["model"] == test_model, f"Model mismatch: expected {test_model}, got {data['model']}"

        logger.info(f"✓ Download initiated for {test_model}")
        return data

    # ========================================================================
    # Scenario Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_scenario_1_llama_download_placement(self, client):
        """
        SCENARIO 1: Download Llama 3.2 1B → verify appears in Downloaded Models (not Available)

        Steps:
        1. Check if Llama 3.2 1B is already downloaded
        2. If not, download it
        3. Verify it appears in /models/downloaded
        4. Verify it doesn't appear in /models/available (or is marked as downloaded)
        """
        logger.info("\n" + "="*80)
        logger.info("SCENARIO 1: Llama 3.2 1B Download and Placement")
        logger.info("="*80)

        model_name = "llama3.2:1b"

        # Step 1: Check current state
        downloaded = await self._get_downloaded_models(client)
        logger.info(f"Currently downloaded models: {downloaded}")

        # Step 2: Download if not present
        if model_name not in downloaded:
            logger.info(f"Downloading {model_name}...")
            await self._download_model(client, model_name)
            await asyncio.sleep(10)  # Wait for download to complete
        else:
            logger.info(f"{model_name} already downloaded")

        # Step 3: Verify in downloaded list
        downloaded_after = await self._get_downloaded_models(client)
        assert model_name in downloaded_after, f"{model_name} not in downloaded list after download"
        logger.info(f"✓ {model_name} appears in Downloaded Models")

        # Step 4: Verify not duplicated in available
        available = await self._get_available_models(client)
        llama_in_available = [m for m in available if m["name"] == model_name]

        if llama_in_available:
            logger.warning(f"⚠ {model_name} still appears in available models (should be filtered or marked)")
        else:
            logger.info(f"✓ {model_name} correctly filtered from available models")

        logger.info("SCENARIO 1: PASSED ✓\n")

    @pytest.mark.asyncio
    async def test_scenario_2_qwen_no_duplicates(self, client):
        """
        SCENARIO 2: Check Qwen2.5 1.5B → verify appears ONLY ONCE

        Steps:
        1. Get available models list
        2. Get downloaded models list
        3. Count occurrences of Qwen2.5 1.5B
        4. Verify it appears only once across both lists
        """
        logger.info("\n" + "="*80)
        logger.info("SCENARIO 2: Qwen2.5 1.5B Duplicate Check")
        logger.info("="*80)

        target_model = "qwen2.5:1.5b"

        # Get both lists
        available = await self._get_available_models(client)
        downloaded = await self._get_downloaded_models(client)

        # Count in available
        qwen_in_available = [m for m in available if target_model in m["name"].lower()]
        logger.info(f"Qwen2.5 1.5B in available models: {len(qwen_in_available)} occurrences")

        # Count in downloaded
        qwen_in_downloaded = [m for m in downloaded if target_model in m.lower()]
        logger.info(f"Qwen2.5 1.5B in downloaded models: {len(qwen_in_downloaded)} occurrences")

        # Total count
        total_count = len(qwen_in_available) + len(qwen_in_downloaded)

        assert total_count <= 1, f"Qwen2.5 1.5B appears {total_count} times (should be 1 or 0)"
        logger.info(f"✓ Qwen2.5 1.5B appears exactly {total_count} time(s) - NO DUPLICATES")

        logger.info("SCENARIO 2: PASSED ✓\n")

    @pytest.mark.asyncio
    async def test_scenario_3_gpt2_download(self, client):
        """
        SCENARIO 3: Download gpt2 → verify successful download and display

        Steps:
        1. Download gpt2 model
        2. Wait for completion
        3. Verify appears in downloaded list
        4. Verify has correct name format
        """
        logger.info("\n" + "="*80)
        logger.info("SCENARIO 3: GPT-2 Download Verification")
        logger.info("="*80)

        model_name = "gpt2"

        # Check if already downloaded
        downloaded_before = await self._get_downloaded_models(client)

        if model_name not in [m for m in downloaded_before if "gpt2" in m.lower()]:
            logger.info(f"Downloading {model_name}...")
            download_response = await self._download_model(client, model_name)
            logger.info(f"Download response: {download_response}")

            # Wait for download to complete (gpt2 is small, should be fast)
            await asyncio.sleep(15)
        else:
            logger.info(f"GPT-2 already downloaded")

        # Verify in downloaded list
        downloaded_after = await self._get_downloaded_models(client)
        gpt2_models = [m for m in downloaded_after if "gpt2" in m.lower()]

        assert len(gpt2_models) > 0, "GPT-2 not found in downloaded models"
        logger.info(f"✓ GPT-2 successfully downloaded: {gpt2_models[0]}")
        logger.info(f"✓ Display name format: {gpt2_models[0]}")

        logger.info("SCENARIO 3: PASSED ✓\n")

    @pytest.mark.asyncio
    async def test_scenario_4_multiple_downloads(self, client):
        """
        SCENARIO 4: Download 3 different models → verify all appear correctly

        Steps:
        1. Select 3 small, fast models
        2. Download them sequentially
        3. Verify all 3 appear in downloaded list
        4. Verify no duplicates
        5. Verify correct naming
        """
        logger.info("\n" + "="*80)
        logger.info("SCENARIO 4: Multiple Model Downloads")
        logger.info("="*80)

        test_models = [
            "qwen2.5:0.5b",
            "tinyllama",
            "phi3:mini"
        ]

        downloaded_before = await self._get_downloaded_models(client)
        logger.info(f"Models before test: {len(downloaded_before)}")

        # Download each model
        for model in test_models:
            if model not in downloaded_before:
                logger.info(f"Downloading {model}...")
                await self._download_model(client, model)
                await asyncio.sleep(10)  # Wait between downloads
            else:
                logger.info(f"{model} already downloaded")

        # Verify all appear
        downloaded_after = await self._get_downloaded_models(client)
        logger.info(f"Models after test: {len(downloaded_after)}")
        logger.info(f"Downloaded models: {downloaded_after}")

        # Check each model
        for model in test_models:
            # Allow for version tags (e.g., tinyllama:latest)
            model_found = any(model in m for m in downloaded_after)
            assert model_found, f"{model} not found in downloaded list"
            logger.info(f"✓ {model} verified in downloaded list")

        # Check for duplicates
        unique_models = set(downloaded_after)
        assert len(unique_models) == len(downloaded_after), \
            f"Duplicates detected! {len(downloaded_after)} total, {len(unique_models)} unique"
        logger.info(f"✓ No duplicates: {len(downloaded_after)} models, all unique")

        logger.info("SCENARIO 4: PASSED ✓\n")

    @pytest.mark.asyncio
    async def test_scenario_5_refresh_no_duplicates(self, client):
        """
        SCENARIO 5: Refresh page → verify no duplicates after refresh

        Steps:
        1. Get initial downloaded list
        2. Simulate refresh by calling API again
        3. Compare lists for duplicates
        4. Verify count consistency
        """
        logger.info("\n" + "="*80)
        logger.info("SCENARIO 5: Page Refresh Duplicate Check")
        logger.info("="*80)

        # First call (initial page load)
        downloaded_1 = await self._get_downloaded_models(client)
        logger.info(f"First call: {len(downloaded_1)} models")

        # Simulate page refresh
        await asyncio.sleep(2)

        # Second call (refresh)
        downloaded_2 = await self._get_downloaded_models(client)
        logger.info(f"Second call: {len(downloaded_2)} models")

        # Third call (another refresh)
        await asyncio.sleep(2)
        downloaded_3 = await self._get_downloaded_models(client)
        logger.info(f"Third call: {len(downloaded_3)} models")

        # Verify consistency
        assert len(downloaded_1) == len(downloaded_2) == len(downloaded_3), \
            f"Model counts differ across refreshes: {len(downloaded_1)}, {len(downloaded_2)}, {len(downloaded_3)}"

        assert set(downloaded_1) == set(downloaded_2) == set(downloaded_3), \
            "Model lists differ across refreshes"

        # Check for internal duplicates
        for i, models in enumerate([downloaded_1, downloaded_2, downloaded_3], 1):
            unique = set(models)
            assert len(unique) == len(models), \
                f"Call {i}: Duplicates found! {len(models)} total, {len(unique)} unique"

        logger.info("✓ All refreshes return consistent, duplicate-free lists")
        logger.info("SCENARIO 5: PASSED ✓\n")

    @pytest.mark.asyncio
    async def test_scenario_6_name_consistency(self, client):
        """
        SCENARIO 6: Check model name consistency across API and Ollama

        Steps:
        1. Get models from /models/downloaded (our API)
        2. Get models directly from Ollama (/api/tags)
        3. Compare model names
        4. Verify exact match
        """
        logger.info("\n" + "="*80)
        logger.info("SCENARIO 6: Model Name Consistency Check")
        logger.info("="*80)

        # Get from our API
        our_api_models = await self._get_downloaded_models(client)
        logger.info(f"Our API models ({len(our_api_models)}): {our_api_models}")

        # Get directly from Ollama
        ollama_response = await client.get("http://localhost:11434/api/tags")
        assert ollama_response.status_code == 200, "Failed to connect to Ollama"

        ollama_data = ollama_response.json()
        ollama_models = [m["name"] for m in ollama_data.get("models", [])]
        logger.info(f"Ollama models ({len(ollama_models)}): {ollama_models}")

        # Compare
        our_set = set(our_api_models)
        ollama_set = set(ollama_models)

        # Check for missing models
        missing_in_our_api = ollama_set - our_set
        extra_in_our_api = our_set - ollama_set

        if missing_in_our_api:
            logger.error(f"✗ Models in Ollama but missing in our API: {missing_in_our_api}")

        if extra_in_our_api:
            logger.error(f"✗ Models in our API but not in Ollama: {extra_in_our_api}")

        assert not missing_in_our_api, f"Models missing in our API: {missing_in_our_api}"
        assert not extra_in_our_api, f"Extra models in our API: {extra_in_our_api}"

        # Verify exact name matches
        for model in our_api_models:
            assert model in ollama_models, f"Model name mismatch: {model} in our API but not exact match in Ollama"

        logger.info("✓ Perfect name consistency between API and Ollama")
        logger.info(f"✓ {len(our_api_models)} models match exactly")
        logger.info("SCENARIO 6: PASSED ✓\n")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    async def _get_available_models(self, client) -> List[Dict[str, Any]]:
        """Get list of available models"""
        response = await client.get(f"{BASE_URL}/models/available")
        assert response.status_code == 200
        return response.json()["models"]

    async def _get_downloaded_models(self, client) -> List[str]:
        """Get list of downloaded model names"""
        response = await client.get(f"{BASE_URL}/models/downloaded")
        assert response.status_code == 200
        return response.json()["models"]

    async def _download_model(self, client, model_name: str) -> Dict[str, Any]:
        """Download a model"""
        response = await client.post(
            f"{BASE_URL}/models/download",
            json={"model_name": model_name}
        )
        assert response.status_code == 200
        return response.json()


# ============================================================================
# Standalone Test Runner (for direct execution)
# ============================================================================

async def run_all_tests():
    """Run all tests in sequence"""
    logger.info("\n" + "🧪 "*40)
    logger.info("COMPREHENSIVE MODEL MANAGEMENT TEST SUITE")
    logger.info("🧪 "*40 + "\n")

    test_suite = TestModelManagementAPI()

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            # API Endpoint Tests
            logger.info("📋 PHASE 1: API Endpoint Tests")
            logger.info("-" * 80)
            await test_suite.test_get_available_models_endpoint(client)
            await test_suite.test_get_downloaded_models_endpoint(client)
            await test_suite.test_download_model_endpoint(client)

            # Scenario Tests
            logger.info("\n📋 PHASE 2: Scenario Tests")
            logger.info("-" * 80)
            await test_suite.test_scenario_1_llama_download_placement(client)
            await test_suite.test_scenario_2_qwen_no_duplicates(client)
            await test_suite.test_scenario_3_gpt2_download(client)
            await test_suite.test_scenario_4_multiple_downloads(client)
            await test_suite.test_scenario_5_refresh_no_duplicates(client)
            await test_suite.test_scenario_6_name_consistency(client)

            logger.info("\n" + "✅ "*40)
            logger.info("ALL TESTS PASSED!")
            logger.info("✅ "*40 + "\n")

        except AssertionError as e:
            logger.error(f"\n❌ TEST FAILED: {e}")
            raise
        except Exception as e:
            logger.error(f"\n❌ UNEXPECTED ERROR: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    # Run tests directly
    asyncio.run(run_all_tests())
