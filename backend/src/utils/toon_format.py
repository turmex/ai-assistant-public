"""
TOON (Token-Optimized Object Notation) Format

Efficient text compression format for reducing token count in LLM conversations.
Inspired by compressed notation techniques while maintaining readability.

Features:
- Abbreviates common words and phrases
- Removes unnecessary articles and conjunctions
- Preserves semantic meaning
- Bidirectional: compress and decompress
"""

import re
from typing import List, Dict, Tuple


# Common word abbreviations
TOON_ABBREVIATIONS = {
    # Articles and conjunctions (can often be removed)
    " the ": " ",
    " a ": " ",
    " an ": " ",
    " and ": " & ",
    " or ": " / ",

    # Common verbs
    " is ": " = ",
    " are ": " = ",
    " was ": " = ",
    " were ": " = ",
    " have ": " hv ",
    " has ": " hz ",
    " will ": " wl ",
    " would ": " wd ",
    " should ": " shd ",
    " could ": " cld ",
    " can ": " cn ",

    # Common words
    " with ": " w/ ",
    " without ": " w/o ",
    " about ": " abt ",
    " please ": " pls ",
    " thank ": " thx ",
    " because ": " bc ",
    " through ": " thru ",
    " between ": " btwn ",
    " your ": " ur ",
    " you are ": " u r ",
    " you're ": " ur ",

    # Technical terms
    " function ": " fn ",
    " variable ": " var ",
    " parameter ": " param ",
    " return ": " ret ",
    " implement ": " impl ",
    " application ": " app ",
    " configuration ": " cfg ",
    " documentation ": " doc ",
    " information ": " info ",
}

# Reverse mapping for decompression
TOON_EXPANSIONS = {v.strip(): k.strip() for k, v in TOON_ABBREVIATIONS.items()}


class TOONFormatter:
    """
    TOON (Token-Optimized Object Notation) formatter.

    Compresses and decompresses text to reduce token count while
    maintaining semantic meaning.
    """

    @staticmethod
    def compress(text: str, aggressive: bool = False) -> str:
        """
        Compress text to TOON format.

        Args:
            text: Input text to compress
            aggressive: If True, apply more aggressive compression

        Returns:
            Compressed text in TOON format
        """
        compressed = text.lower()

        # Apply abbreviations
        for full, abbrev in TOON_ABBREVIATIONS.items():
            compressed = compressed.replace(full, abbrev)

        if aggressive:
            # More aggressive: remove common punctuation
            compressed = re.sub(r'[,;:]', '', compressed)
            # Collapse multiple spaces
            compressed = re.sub(r'\s+', ' ', compressed)

        # Trim and return
        return compressed.strip()

    @staticmethod
    def decompress(toon_text: str) -> str:
        """
        Decompress TOON format back to readable text.

        Args:
            toon_text: TOON-formatted text

        Returns:
            Decompressed readable text
        """
        decompressed = toon_text

        # Apply expansions (reverse of abbreviations)
        for abbrev, full in TOON_EXPANSIONS.items():
            # Add spaces around abbreviation for matching
            pattern = f" {re.escape(abbrev)} "
            replacement = f" {full} "
            decompressed = decompressed.replace(pattern, replacement)

        # Clean up spacing
        decompressed = re.sub(r'\s+', ' ', decompressed)

        return decompressed.strip()

    @staticmethod
    def estimate_token_savings(original: str, compressed: str) -> Dict[str, any]:
        """
        Estimate token savings from compression.

        Args:
            original: Original text
            compressed: Compressed text

        Returns:
            Dict with savings statistics
        """
        # Rough token estimate (1 token ≈ 4 characters)
        original_tokens = len(original) / 4
        compressed_tokens = len(compressed) / 4
        saved_tokens = original_tokens - compressed_tokens
        savings_percent = (saved_tokens / original_tokens * 100) if original_tokens > 0 else 0

        return {
            "original_length": len(original),
            "compressed_length": len(compressed),
            "original_tokens_estimate": int(original_tokens),
            "compressed_tokens_estimate": int(compressed_tokens),
            "tokens_saved": int(saved_tokens),
            "savings_percent": round(savings_percent, 1)
        }

    @staticmethod
    def compress_conversation(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Compress an entire conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            List of messages with compressed content
        """
        compressed_messages = []

        for msg in messages:
            compressed_msg = msg.copy()
            if 'content' in msg:
                compressed_msg['content'] = TOONFormatter.compress(msg['content'])
            compressed_messages.append(compressed_msg)

        return compressed_messages

    @staticmethod
    def should_use_toon(text: str, threshold_length: int = 200) -> bool:
        """
        Determine if TOON compression is beneficial.

        Args:
            text: Text to evaluate
            threshold_length: Minimum length to consider compression

        Returns:
            bool: True if TOON compression is recommended
        """
        # Only use TOON for longer texts where savings matter
        if len(text) < threshold_length:
            return False

        # Check if text has compressible content
        compressible_count = sum(
            text.lower().count(pattern.strip())
            for pattern in TOON_ABBREVIATIONS.keys()
        )

        # Use TOON if we find at least 5 compressible patterns
        return compressible_count >= 5


# Example usage
if __name__ == "__main__":
    # Example text
    original = "Please implement a function that will return the configuration for the application. The function should have parameters for the settings and it should validate the information."

    formatter = TOONFormatter()
    compressed = formatter.compress(original)
    decompressed = formatter.decompress(compressed)
    stats = formatter.estimate_token_savings(original, compressed)

    print("Original:")
    print(original)
    print(f"\nCompressed (TOON):")
    print(compressed)
    print(f"\nDecompressed:")
    print(decompressed)
    print(f"\nSavings:")
    print(f"  Tokens saved: {stats['tokens_saved']} ({stats['savings_percent']}%)")
    print(f"  Original: {stats['original_tokens_estimate']} tokens")
    print(f"  Compressed: {stats['compressed_tokens_estimate']} tokens")
