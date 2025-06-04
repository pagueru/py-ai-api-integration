INSERT INTO api_usages (
    id,
    created_at,
    model,
    system_fingerprint,
    prompt,
    completion,
    prompt_tokens,
    completion_tokens,
    total_tokens,
    cached_tokens,
    cache_hit_tokens,
    cache_miss_tokens,
    finish_reason,
    logprobs
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
