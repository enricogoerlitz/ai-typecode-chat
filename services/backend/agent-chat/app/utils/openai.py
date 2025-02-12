import tiktoken


def trim_to_token_limit(
        text,
        max_tokens=8000,
        model="text-embedding-3-large"
) -> str:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return text

    trimmed_text = encoding.decode(tokens[:max_tokens])

    return trimmed_text
