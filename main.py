
import argparse
import json
from pathlib import Path


def get_token_encoder(tokenizer: str | None = None):

    tokenizer = (tokenizer or "gpt2").lower()

    if tokenizer == "gpt2":
        from transformers import GPT2TokenizerFast
        tok = GPT2TokenizerFast.from_pretrained("gpt2")
        return lambda s: len(tok.encode(s))

    # otherwise: tiktoken
    import tiktoken

    enc = tiktoken.get_encoding("gpt2")
    return lambda s: len(enc.encode(s))


def main():

    jsonl_path = "wordacy.jsonl"
    field ="example"

    skip_nonstring = True


    count_encoder = get_token_encoder()

    total_tokens = 0
    path = Path(jsonl_path)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            val = obj.get(field)
            if val is None or val == "":
                continue
            if not isinstance(val, str):
                if skip_nonstring:
                    continue
                val = str(val)
            total_tokens += count_encoder(val)

    print("wordacy.jsonl: tokens =", total_tokens)


if __name__ == "__main__":
    main()
