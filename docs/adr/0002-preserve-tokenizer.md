# ADR-0002: preserve upstream tokenizer

Status: accepted.

The pinned SmolLM2-135M tokenizer and its ChatML delimiter vocabulary are kept
unchanged. The project uses a versioned renderer because the current pinned
tokenizer configuration does not provide a `chat_template` field. A tokenizer
change would require a new parameter-count, compatibility, and ablation record.
