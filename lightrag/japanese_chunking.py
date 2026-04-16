"""
Japanese-aware text chunking for LightRAG.

Splits text at natural Japanese sentence boundaries (。！？etc.) before
applying token-size limits, producing semantically coherent chunks that
improve embedding quality for Japanese documents.

Usage:
    from lightrag.japanese_chunking import japanese_chunking

    rag = LightRAG(
        chunking_func=japanese_chunking,
        ...
    )
"""

from __future__ import annotations

import re
from typing import Any

from lightrag.utils import Tokenizer

# Japanese sentence-ending patterns:
#   。！？ followed by optional closing brackets/quotes, then whitespace or EOL
_SENTENCE_BOUNDARY_RE = re.compile(
    r"(?<=[。！？\!\?])"  # after sentence-ending punctuation
    r"[」』）\)）】〉》\]]*"  # optional closing brackets/quotes
    r"[\s]*"  # optional whitespace
    r"(?=\S)"  # lookahead: next non-whitespace char (prevents splitting at end)
)

# Fallback: split on newlines (paragraph boundaries)
_PARAGRAPH_BOUNDARY_RE = re.compile(r"\n+")


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using Japanese-aware boundaries.

    Strategy:
    1. Split by paragraph (double newline) first
    2. Within each paragraph, split by Japanese sentence boundaries
    3. Preserve all content (no text is lost)
    """
    paragraphs = _PARAGRAPH_BOUNDARY_RE.split(text)
    sentences: list[str] = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        parts = _SENTENCE_BOUNDARY_RE.split(para)
        for part in parts:
            part = part.strip()
            if part:
                sentences.append(part)
    return sentences


def _merge_short_sentences(
    sentences: list[str],
    tokenizer: Tokenizer,
    min_tokens: int = 20,
) -> list[str]:
    """Merge very short sentences to avoid tiny chunks."""
    if not sentences:
        return sentences

    merged: list[str] = []
    buffer = sentences[0]

    for sent in sentences[1:]:
        buf_tokens = len(tokenizer.encode(buffer))
        if buf_tokens < min_tokens:
            buffer = buffer + sent
        else:
            merged.append(buffer)
            buffer = sent

    if buffer:
        merged.append(buffer)
    return merged


def japanese_chunking(
    tokenizer: Tokenizer,
    content: str,
    split_by_character: str | None = None,
    split_by_character_only: bool = False,
    chunk_overlap_token_size: int = 100,
    chunk_token_size: int = 1200,
) -> list[dict[str, Any]]:
    """Japanese-aware chunking function compatible with LightRAG's chunking_func interface.

    Algorithm:
    1. Split content into sentences at Japanese boundaries (。！？) and paragraphs
    2. Merge very short sentences to avoid fragments
    3. Greedily pack sentences into chunks up to chunk_token_size
    4. Add overlap by prepending trailing sentences from the previous chunk
    5. If a single sentence exceeds chunk_token_size, fall back to token-window splitting

    Args:
        tokenizer: LightRAG Tokenizer instance
        content: Full text to chunk
        split_by_character: Ignored (Japanese boundaries used instead)
        split_by_character_only: Ignored
        chunk_overlap_token_size: Token overlap between consecutive chunks
        chunk_token_size: Maximum tokens per chunk

    Returns:
        List of dicts with keys: tokens, content, chunk_order_index
    """
    # Split into sentences
    sentences = _split_into_sentences(content)
    if not sentences:
        return []

    # Merge very short sentences
    sentences = _merge_short_sentences(sentences, tokenizer, min_tokens=20)

    # Pre-compute token counts for each sentence
    sent_tokens = [len(tokenizer.encode(s)) for s in sentences]

    results: list[dict[str, Any]] = []
    chunk_index = 0
    i = 0

    while i < len(sentences):
        chunk_sents: list[str] = []
        chunk_tok_count = 0

        # Add overlap from previous chunk's tail
        if results and chunk_overlap_token_size > 0:
            # Walk backward through previous chunk's sentences to build overlap
            prev_sents = results[-1]["_sentences"]
            overlap_sents: list[str] = []
            overlap_tok = 0
            for ps in reversed(prev_sents):
                ps_tok = len(tokenizer.encode(ps))
                if overlap_tok + ps_tok > chunk_overlap_token_size:
                    break
                overlap_sents.insert(0, ps)
                overlap_tok += ps_tok
            chunk_sents.extend(overlap_sents)
            chunk_tok_count += overlap_tok

        # Pack sentences greedily
        packed_sents: list[str] = []
        while i < len(sentences):
            s_tok = sent_tokens[i]

            # Handle oversized single sentence via token-window fallback.
            # Only gate on packed_sents (not chunk_sents): if overlap content
            # has been prepended for this chunk, discard it and take the
            # fallback path. Otherwise the outer loop would re-enter with
            # i unchanged (overlap occupies chunk_tok_count, the oversized
            # sentence cannot fit, packed_sents stays empty, no chunk is
            # appended, and i never advances → infinite loop).
            # Cross-chunk continuity at this boundary is acceptable to lose
            # because the oversized sentence's own window overlap preserves
            # continuity within its split.
            if s_tok > chunk_token_size and not packed_sents:
                tokens = tokenizer.encode(sentences[i])
                for start in range(
                    0, len(tokens), chunk_token_size - chunk_overlap_token_size
                ):
                    window = tokens[start : start + chunk_token_size]
                    text = tokenizer.decode(window).strip()
                    if text:
                        results.append(
                            {
                                "tokens": len(window),
                                "content": text,
                                "chunk_order_index": chunk_index,
                                "_sentences": [text],
                            }
                        )
                        chunk_index += 1
                i += 1
                break

            if chunk_tok_count + s_tok > chunk_token_size:
                break

            packed_sents.append(sentences[i])
            chunk_tok_count += s_tok
            i += 1

        if packed_sents:
            all_sents = chunk_sents + packed_sents
            chunk_text = "".join(all_sents).strip()
            if chunk_text:
                actual_tokens = len(tokenizer.encode(chunk_text))
                results.append(
                    {
                        "tokens": actual_tokens,
                        "content": chunk_text,
                        "chunk_order_index": chunk_index,
                        "_sentences": packed_sents,
                    }
                )
                chunk_index += 1

    # Remove internal _sentences key before returning
    for r in results:
        r.pop("_sentences", None)

    return results
