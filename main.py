
import argparse
import json
from pathlib import Path


def get_token_counter(tokenizer: str, model: str | None, encoding_name: str | None):
    if tokenizer.lower() == "gpt2":
        from transformers import GPT2TokenizerFast
        tok = GPT2TokenizerFast.from_pretrained("gpt2")
        return lambda s: len(tok.encode(s))

    # otherwise: tiktoken
    import tiktoken
    if encoding_name:
        enc = tiktoken.get_encoding(encoding_name)
    elif model:
        enc = tiktoken.encoding_for_model(model)
    else:
        enc = tiktoken.get_encoding("cl100k_base")
    return lambda s: len(enc.encode(s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl_path")
    ap.add_argument("--field", default="example")
    ap.add_argument("--tokenizer", default="tiktoken", choices=["tiktoken", "gpt2"])
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--encoding", default=None)
    ap.add_argument("--skip-nonstring", action="store_true")
    args = ap.parse_args()

    count_tokens = get_token_counter(args.tokenizer, args.model, args.encoding)

    total_tokens = 0
    path = Path(args.jsonl_path)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            val = obj.get(args.field)
            if val is None or val == "":
                continue
            if not isinstance(val, str):
                if args.skip_nonstring:
                    continue
                val = str(val)
            total_tokens += count_tokens(val)

    print(total_tokens)


if __name__ == "__main__":
    main()
