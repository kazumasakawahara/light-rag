"""Regression tests for lightrag.japanese_chunking.

Covers the three user-requested regression areas (Japanese sentence
boundaries, English-mixed content, and oversized sentences) plus
supporting invariants (chunk structure, overlap, short-sentence merging,
paragraph boundaries, closing brackets).

All tests are offline and use a DummyTokenizer that maps each character
to a single token via ord(). This keeps token math trivial while still
exercising the sentence-aware packing logic.
"""

import pytest

from lightrag.japanese_chunking import japanese_chunking
from lightrag.utils import Tokenizer, TokenizerInterface


class DummyTokenizer(TokenizerInterface):
    """1 character = 1 token. Works with Japanese codepoints via ord()."""

    def encode(self, content: str):
        return [ord(ch) for ch in content]

    def decode(self, tokens):
        return "".join(chr(token) for token in tokens)


def make_tokenizer() -> Tokenizer:
    return Tokenizer(model_name="dummy", tokenizer=DummyTokenizer())


def _make_sentence(prefix: str, length: int, terminator: str = "。") -> str:
    """Build a sentence of exactly `length` tokens ending with `terminator`.

    `length` counts the terminator, so the filler length is length - len(terminator).
    """
    filler_len = length - len(terminator)
    assert filler_len > 0, "length must exceed terminator length"
    return prefix * filler_len + terminator


# ============================================================================
# Sentence boundary recognition: 。！？
# ============================================================================


@pytest.mark.offline
def test_kuten_splits_sentences():
    """Sentences separated by 。 are packed without loss of punctuation."""
    tokenizer = make_tokenizer()
    # Three 30-token sentences. chunk_size=60 fits exactly two per chunk.
    s1 = _make_sentence("a", 30)
    s2 = _make_sentence("b", 30)
    s3 = _make_sentence("c", 30)
    content = s1 + s2 + s3

    chunks = japanese_chunking(
        tokenizer,
        content,
        chunk_token_size=60,
        chunk_overlap_token_size=0,
    )

    assert len(chunks) == 2
    assert chunks[0]["content"] == s1 + s2
    assert chunks[1]["content"] == s3
    # Punctuation preserved with the sentence it terminates
    assert chunks[0]["content"].count("。") == 2
    assert chunks[1]["content"].endswith("。")


@pytest.mark.offline
def test_exclamation_mark_splits_sentences():
    """Full-width ！ is recognized as a sentence boundary."""
    tokenizer = make_tokenizer()
    s1 = _make_sentence("a", 30, terminator="！")
    s2 = _make_sentence("b", 30, terminator="！")
    s3 = _make_sentence("c", 30, terminator="！")

    chunks = japanese_chunking(
        tokenizer,
        s1 + s2 + s3,
        chunk_token_size=60,
        chunk_overlap_token_size=0,
    )

    assert len(chunks) == 2
    assert chunks[0]["content"] == s1 + s2
    assert chunks[1]["content"] == s3


@pytest.mark.offline
def test_question_mark_splits_sentences():
    """Full-width ？ is recognized as a sentence boundary."""
    tokenizer = make_tokenizer()
    s1 = _make_sentence("a", 30, terminator="？")
    s2 = _make_sentence("b", 30, terminator="？")

    chunks = japanese_chunking(
        tokenizer,
        s1 + s2,
        chunk_token_size=60,
        chunk_overlap_token_size=0,
    )

    assert len(chunks) == 1
    assert chunks[0]["content"] == s1 + s2


@pytest.mark.offline
def test_halfwidth_punctuation_splits_sentences():
    """Half-width ! and ? also act as boundaries (per regex)."""
    tokenizer = make_tokenizer()
    s1 = _make_sentence("a", 30, terminator="!")
    s2 = _make_sentence("b", 30, terminator="?")
    s3 = _make_sentence("c", 30, terminator="。")

    chunks = japanese_chunking(
        tokenizer,
        s1 + s2 + s3,
        chunk_token_size=60,
        chunk_overlap_token_size=0,
    )

    # Each sentence is 30 tokens; chunk_size=60 packs two per chunk.
    assert len(chunks) == 2
    assert chunks[0]["content"] == s1 + s2
    assert chunks[1]["content"] == s3


@pytest.mark.offline
def test_closing_brackets_after_punctuation():
    """Closing brackets following 。 are consumed as part of the boundary.

    Implementation note: the regex consumes 」『』）】 etc. as separators,
    so the bracket is dropped from output. This test documents the current
    behavior to catch unintended regressions.
    """
    tokenizer = make_tokenizer()
    content = "これは引用です。」次の文が始まります。"

    chunks = japanese_chunking(
        tokenizer,
        content,
        chunk_token_size=200,
        chunk_overlap_token_size=0,
    )

    assert len(chunks) == 1
    # Both sentences appear, but the 」 between them is consumed by the split.
    assert "これは引用です。" in chunks[0]["content"]
    assert "次の文が始まります。" in chunks[0]["content"]
    assert "」" not in chunks[0]["content"]


# ============================================================================
# Mixed Japanese + English content
# ============================================================================


@pytest.mark.offline
def test_mixed_japanese_and_english():
    """Japanese and English sentences are split at their respective terminators."""
    tokenizer = make_tokenizer()
    jp = _make_sentence("あ", 30, terminator="。")
    en = _make_sentence("b", 30, terminator=".")

    # Note: '.' is not a recognized boundary, so "b...b." stays as one sentence.
    # Put the English sentence first (no split inside) followed by Japanese.
    chunks = japanese_chunking(
        tokenizer,
        en + jp,
        chunk_token_size=200,
        chunk_overlap_token_size=0,
    )

    assert len(chunks) == 1
    # Both segments preserved
    assert en in chunks[0]["content"]
    assert jp in chunks[0]["content"]


@pytest.mark.offline
def test_english_sentences_with_halfwidth_punctuation():
    """English sentences ending with ! or ? split via half-width boundaries."""
    tokenizer = make_tokenizer()
    s1 = _make_sentence("a", 30, terminator="!")
    s2 = _make_sentence("b", 30, terminator="?")
    jp = _make_sentence("あ", 30, terminator="。")

    chunks = japanese_chunking(
        tokenizer,
        s1 + s2 + jp,
        chunk_token_size=60,
        chunk_overlap_token_size=0,
    )

    assert len(chunks) == 2
    assert chunks[0]["content"] == s1 + s2
    assert chunks[1]["content"] == jp


# ============================================================================
# Oversized single sentence: token-window fallback
# ============================================================================


@pytest.mark.offline
def test_oversized_single_sentence_falls_back_to_token_window():
    """A sentence larger than chunk_token_size is split via token windows."""
    tokenizer = make_tokenizer()
    # 1500 tokens of filler + 。 = 1501 tokens total. chunk_size=1200, overlap=100.
    content = _make_sentence("a", 1501, terminator="。")

    chunks = japanese_chunking(
        tokenizer,
        content,
        chunk_token_size=1200,
        chunk_overlap_token_size=100,
    )

    # step = chunk_size - overlap = 1100
    # windows start at 0, 1100 → 2 chunks
    assert len(chunks) == 2
    assert chunks[0]["tokens"] == 1200
    # Second window: tokens[1100:2300] but only 1501 tokens exist → 401 tokens
    assert chunks[1]["tokens"] == 401
    # Chunks are contiguous slices of the original content
    assert chunks[0]["content"] + chunks[1]["content"][100:] == content


@pytest.mark.offline
def test_oversized_sentence_as_first_then_normal_sentences():
    """After processing an oversized first sentence, normal packing resumes."""
    tokenizer = make_tokenizer()
    huge = _make_sentence("a", 1501, terminator="。")
    s2 = _make_sentence("b", 30, terminator="。")
    s3 = _make_sentence("c", 30, terminator="。")

    chunks = japanese_chunking(
        tokenizer,
        huge + s2 + s3,
        chunk_token_size=1200,
        chunk_overlap_token_size=0,
    )

    # 2 chunks from the huge sentence + 1 chunk packing s2+s3
    assert len(chunks) == 3
    assert chunks[2]["content"] == s2 + s3


@pytest.mark.offline
def test_oversized_sentence_after_normal_with_overlap_does_not_hang():
    """Regression: overlap + mid-stream oversized sentence must terminate.

    Prior to the fix, the oversized-fallback branch was gated on both
    `not chunk_sents` and `not packed_sents`. When overlap was enabled and
    a prior chunk existed, entering a new iteration populated chunk_sents
    with overlap content; if the next sentence exceeded chunk_token_size,
    the fallback was skipped and the regular packing break triggered,
    leaving packed_sents empty. No chunk was appended and i never
    advanced, causing an infinite loop.

    If this test hangs, the regression has returned. A well-behaved
    implementation must advance through the oversized sentence.
    """
    tokenizer = make_tokenizer()
    s1 = _make_sentence("a", 30, terminator="。")
    huge = _make_sentence("b", 150, terminator="。")  # > chunk_token_size=60
    s3 = _make_sentence("c", 30, terminator="。")

    chunks = japanese_chunking(
        tokenizer,
        s1 + huge + s3,
        chunk_token_size=60,
        chunk_overlap_token_size=35,  # non-zero: triggers the buggy path
    )

    # Must terminate and produce a sensible split:
    # chunk 0: s1 (30 tokens)
    # chunks 1..N: token-window slices of huge (chunk_size=60, step=25)
    # final chunk: s3 (possibly with overlap from last huge window)
    assert len(chunks) >= 3

    # chunk_order_index must remain sequential despite the fallback path
    assert [c["chunk_order_index"] for c in chunks] == list(range(len(chunks)))

    # Content preservation: s1 appears in the first chunk, s3 in the last
    assert chunks[0]["content"] == s1
    assert s3 in chunks[-1]["content"]

    # The huge sentence's terminator must appear somewhere across chunks
    combined = "".join(c["content"] for c in chunks)
    assert "。" in combined
    # All three sentences contribute content
    assert combined.count("a") >= 29  # s1 filler
    assert combined.count("b") >= 149  # huge filler (appears in multiple windows)
    assert combined.count("c") >= 29  # s3 filler


# ============================================================================
# Paragraph boundaries (\n\n) and whitespace
# ============================================================================


@pytest.mark.offline
def test_paragraph_boundary_splits_before_sentence_boundary():
    """Paragraphs (\\n\\n) are split first, then sentences within each paragraph."""
    tokenizer = make_tokenizer()
    p1 = _make_sentence("a", 30, terminator="。")
    p2 = _make_sentence("b", 30, terminator="。")
    content = p1 + "\n\n" + p2

    chunks = japanese_chunking(
        tokenizer,
        content,
        chunk_token_size=60,
        chunk_overlap_token_size=0,
    )

    # Both sentences fit in one chunk (60 tokens total, no newlines in output)
    assert len(chunks) == 1
    # Paragraph separators are dropped; sentences are concatenated
    assert chunks[0]["content"] == p1 + p2


@pytest.mark.offline
def test_whitespace_between_sentences_is_stripped():
    """Whitespace between sentences is consumed by the boundary regex."""
    tokenizer = make_tokenizer()
    s1 = _make_sentence("a", 30, terminator="。")
    s2 = _make_sentence("b", 30, terminator="。")

    chunks = japanese_chunking(
        tokenizer,
        s1 + "   " + s2,
        chunk_token_size=200,
        chunk_overlap_token_size=0,
    )

    assert len(chunks) == 1
    assert chunks[0]["content"] == s1 + s2


# ============================================================================
# Short-sentence merging
# ============================================================================


@pytest.mark.offline
def test_short_sentences_are_merged():
    """Sentences shorter than 20 tokens are merged by _merge_short_sentences."""
    tokenizer = make_tokenizer()
    # Three 5-token sentences; each is below the 20-token merge threshold.
    s1 = _make_sentence("a", 5, terminator="。")
    s2 = _make_sentence("b", 5, terminator="。")
    s3 = _make_sentence("c", 5, terminator="。")

    chunks = japanese_chunking(
        tokenizer,
        s1 + s2 + s3,
        chunk_token_size=200,
        chunk_overlap_token_size=0,
    )

    # All three merge into a single chunk (merge happens before packing).
    assert len(chunks) == 1
    assert chunks[0]["content"] == s1 + s2 + s3


# ============================================================================
# Overlap behavior
# ============================================================================


@pytest.mark.offline
def test_overlap_includes_trailing_sentence_from_previous_chunk():
    """Overlap prepends the prior chunk's trailing sentence(s) within budget."""
    tokenizer = make_tokenizer()
    s1 = _make_sentence("a", 30, terminator="。")
    s2 = _make_sentence("b", 30, terminator="。")
    s3 = _make_sentence("c", 30, terminator="。")

    # overlap=35 is enough for one 30-token sentence but not two.
    chunks = japanese_chunking(
        tokenizer,
        s1 + s2 + s3,
        chunk_token_size=60,
        chunk_overlap_token_size=35,
    )

    assert len(chunks) == 2
    assert chunks[0]["content"] == s1 + s2
    # Second chunk prepends s2 (the tail of chunk 0) then adds s3.
    assert chunks[1]["content"] == s2 + s3


@pytest.mark.offline
def test_zero_overlap_produces_disjoint_chunks():
    """With overlap=0, chunks share no sentences."""
    tokenizer = make_tokenizer()
    s1 = _make_sentence("a", 30, terminator="。")
    s2 = _make_sentence("b", 30, terminator="。")
    s3 = _make_sentence("c", 30, terminator="。")

    chunks = japanese_chunking(
        tokenizer,
        s1 + s2 + s3,
        chunk_token_size=60,
        chunk_overlap_token_size=0,
    )

    assert len(chunks) == 2
    assert chunks[0]["content"] == s1 + s2
    assert chunks[1]["content"] == s3


# ============================================================================
# Chunk structure invariants
# ============================================================================


@pytest.mark.offline
def test_chunk_structure_has_required_keys_and_no_internal_leak():
    """Returned chunks expose tokens/content/chunk_order_index only."""
    tokenizer = make_tokenizer()
    s1 = _make_sentence("a", 30, terminator="。")
    s2 = _make_sentence("b", 30, terminator="。")

    chunks = japanese_chunking(
        tokenizer,
        s1 + s2,
        chunk_token_size=60,
        chunk_overlap_token_size=0,
    )

    assert len(chunks) == 1
    chunk = chunks[0]
    assert set(chunk.keys()) == {"tokens", "content", "chunk_order_index"}
    # Internal bookkeeping key must not leak to callers.
    assert "_sentences" not in chunk


@pytest.mark.offline
def test_chunk_order_index_is_sequential():
    """chunk_order_index increments by 1 across all produced chunks."""
    tokenizer = make_tokenizer()
    sentences = [_make_sentence(chr(ord("a") + i), 30) for i in range(5)]

    chunks = japanese_chunking(
        tokenizer,
        "".join(sentences),
        chunk_token_size=60,
        chunk_overlap_token_size=0,
    )

    assert [c["chunk_order_index"] for c in chunks] == list(range(len(chunks)))


@pytest.mark.offline
def test_chunk_tokens_matches_content_length():
    """Reported token count equals tokenizer.encode(content) length."""
    tokenizer = make_tokenizer()
    s1 = _make_sentence("a", 30, terminator="。")
    s2 = _make_sentence("b", 30, terminator="。")

    chunks = japanese_chunking(
        tokenizer,
        s1 + s2,
        chunk_token_size=200,
        chunk_overlap_token_size=0,
    )

    for chunk in chunks:
        assert chunk["tokens"] == len(tokenizer.encode(chunk["content"]))


# ============================================================================
# Edge cases
# ============================================================================


@pytest.mark.offline
def test_empty_content_returns_empty_list():
    tokenizer = make_tokenizer()
    assert japanese_chunking(tokenizer, "") == []


@pytest.mark.offline
def test_whitespace_only_content_returns_empty_list():
    tokenizer = make_tokenizer()
    assert japanese_chunking(tokenizer, "   \n\n  \t  ") == []


@pytest.mark.offline
def test_content_without_sentence_boundary_is_treated_as_one_sentence():
    """No 。！？ → treated as one sentence; oversized triggers token-window split."""
    tokenizer = make_tokenizer()
    # 50 tokens, no terminator. chunk_size=30 forces token-window fallback.
    content = "a" * 50

    chunks = japanese_chunking(
        tokenizer,
        content,
        chunk_token_size=30,
        chunk_overlap_token_size=0,
    )

    # step = 30, windows at 0, 30 → 2 chunks of 30 and 20 tokens.
    assert len(chunks) == 2
    assert chunks[0]["tokens"] == 30
    assert chunks[1]["tokens"] == 20


@pytest.mark.offline
def test_content_without_boundary_fits_in_one_chunk():
    """Short boundaryless text yields a single chunk."""
    tokenizer = make_tokenizer()
    content = "a" * 50

    chunks = japanese_chunking(
        tokenizer,
        content,
        chunk_token_size=200,
        chunk_overlap_token_size=0,
    )

    assert len(chunks) == 1
    assert chunks[0]["content"] == content
    assert chunks[0]["tokens"] == 50
