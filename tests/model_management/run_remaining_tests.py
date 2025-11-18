#!/usr/bin/env python3
"""
Run remaining tests that were interrupted by duplicate detection
"""

import asyncio
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
TIMEOUT = 120.0


async def test_scenario_5_refresh_no_duplicates():
    """SCENARIO 5: Refresh page → verify no duplicates after refresh"""
    logger.info("\n" + "="*80)
    logger.info("SCENARIO 5: Page Refresh Duplicate Check")
    logger.info("="*80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # First call (initial page load)
        r1 = await client.get(f"{BASE_URL}/models/downloaded")
        downloaded_1 = r1.json()["models"]
        logger.info(f"First call: {len(downloaded_1)} models")

        # Simulate page refresh
        await asyncio.sleep(2)

        # Second call (refresh)
        r2 = await client.get(f"{BASE_URL}/models/downloaded")
        downloaded_2 = r2.json()["models"]
        logger.info(f"Second call: {len(downloaded_2)} models")

        # Third call (another refresh)
        await asyncio.sleep(2)
        r3 = await client.get(f"{BASE_URL}/models/downloaded")
        downloaded_3 = r3.json()["models"]
        logger.info(f"Third call: {len(downloaded_3)} models")

        # Verify consistency
        assert len(downloaded_1) == len(downloaded_2) == len(downloaded_3), \
            f"Model counts differ: {len(downloaded_1)}, {len(downloaded_2)}, {len(downloaded_3)}"

        assert set(downloaded_1) == set(downloaded_2) == set(downloaded_3), \
            "Model lists differ across refreshes"

        # Check for internal duplicates
        for i, models in enumerate([downloaded_1, downloaded_2, downloaded_3], 1):
            unique = set(models)
            assert len(unique) == len(models), \
                f"Call {i}: Duplicates found! {len(models)} total, {len(unique)} unique"

        logger.info("✓ All refreshes return consistent, duplicate-free lists")
        logger.info("SCENARIO 5: PASSED ✓\n")


async def test_scenario_6_name_consistency():
    """SCENARIO 6: Check model name consistency across API and Ollama"""
    logger.info("\n" + "="*80)
    logger.info("SCENARIO 6: Model Name Consistency Check")
    logger.info("="*80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Get from our API
        r1 = await client.get(f"{BASE_URL}/models/downloaded")
        our_api_models = r1.json()["models"]
        logger.info(f"Our API models ({len(our_api_models)}): {our_api_models}")

        # Get directly from Ollama
        r2 = await client.get("http://localhost:11434/api/tags")
        assert r2.status_code == 200, "Failed to connect to Ollama"

        ollama_data = r2.json()
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

        assert not missing_in_our_api, f"Models missing: {missing_in_our_api}"
        assert not extra_in_our_api, f"Extra models: {extra_in_our_api}"

        # Verify exact name matches
        for model in our_api_models:
            assert model in ollama_models, f"Mismatch: {model}"

        logger.info("✓ Perfect name consistency between API and Ollama")
        logger.info(f"✓ {len(our_api_models)} models match exactly")
        logger.info("SCENARIO 6: PASSED ✓\n")


async def main():
    """Run remaining tests"""
    logger.info("\n🧪 RUNNING REMAINING TESTS\n")

    try:
        await test_scenario_5_refresh_no_duplicates()
        await test_scenario_6_name_consistency()

        logger.info("\n✅ ALL REMAINING TESTS PASSED!\n")
        return 0

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
