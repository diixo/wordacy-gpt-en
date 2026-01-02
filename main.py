
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


def txt_to_jsonl(in_path: str, out_path: str, encoding: str = "utf-8") -> None:
    with open(in_path, "r", encoding=encoding) as fin, open(out_path, "w", encoding=encoding) as fout:
        for line in fin:
            txt = line.strip()

            if not txt:
                continue

            pos = txt.find(" is ")
            subject = None
            if pos > 0:
                subject = txt[0:pos]

            if subject is not None:
                rec = {"verb": "", "meaning": f'definition of "{subject}"', "example": txt}
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main():

    #txt_to_jsonl("input.txt", "output.jsonl")
    #exit(0)

    jsonl_path = "wordacy.jsonl"

    skip_nonstring = True
    def_dict = dict()

    count_encoder = get_token_encoder()

    total_tokens = 0
    path = Path(jsonl_path)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)

            val = obj.get("example")
            definition = obj.get("meaning")

            if (definition is not None) and (definition != "") and (definition.find("definition") == 0):
                if definition not in def_dict:
                    def_dict[definition] = "meaning"
                else:
                    print(definition)

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
