
import json
import re
from typing import Dict, List

# --------- Simple English inflection helpers (for regular verbs) ---------

def third_person_singular(base: str) -> str:
    # rules: go -> goes, watch -> watches, try -> tries, play -> plays
    if re.search(r"(s|x|z|ch|sh)$", base):
        return base + "es"
    if re.search(r"[^aeiou]y$", base):
        return base[:-1] + "ies"
    if base.endswith("o"):
        return base + "es"
    return base + "s"

def present_participle(base: str) -> str:
    # rules: make -> making, die -> dying, run -> running (doubling is hard; we keep it simple)
    if base.endswith("ie"):
        return base[:-2] + "ying"
    if base.endswith("e") and not base.endswith("ee"):
        return base[:-1] + "ing"
    return base + "ing"

def past_tense_regular(base: str) -> str:
    # rules: play -> played, stop -> stopped (doubling not handled), study -> studied
    if base.endswith("e"):
        return base + "d"
    if re.search(r"[^aeiou]y$", base):
        return base[:-1] + "ied"
    return base + "ed"

def past_participle_regular(base: str) -> str:
    # for regular verbs, same as past tense
    return past_tense_regular(base)

# --------- Build forms table ---------

def build_forms(base: str, irregular: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """
    Returns dict with keys:
    base, past, pp, s3, ing
    """
    if base in irregular:
        forms = irregular[base].copy()
        forms.setdefault("base", base)
        # derive any missing using regular rules
        forms.setdefault("s3", third_person_singular(base))
        forms.setdefault("ing", present_participle(base))
        forms.setdefault("past", past_tense_regular(base))
        forms.setdefault("pp", past_participle_regular(base))
        return forms

    return {
        "base": base,
        "past": past_tense_regular(base),
        "pp": past_participle_regular(base),
        "s3": third_person_singular(base),
        "ing": present_participle(base),
    }

# --------- Dataset templates (21 examples per verb) ---------

TEMPLATES = [
    ("Give me the base form of the verb \"{v}\".", "{base}"),

    ("Give me the past tense form of the verb \"{v}\".", "{past}"),
    ("What is the past tense of the verb \"{v}\"?", "{past}"),

    ("Give me the past participle form of the verb \"{v}\".", "{pp}"),
    ("What is the past participle of the verb \"{v}\"?", "{pp}"),

    ("Give me the third-person singular present form of the verb \"{v}\".", "{s3}"),
    ("Conjugate the verb \"{v}\" for he/she/it (present simple).", "{s3}"),

    ("Give me the present participle (gerund) form of the verb \"{v}\".", "{ing}"),
    ("What is the -ing form of the verb \"{v}\"?", "{ing}"),

    ("Give me all past forms in order: past tense, past participle, of the verb \"{v}\".", "{past},{pp}"),
    ("Give me all present forms in order: third-person singular present, present participle, of the verb \"{v}\".", "{s3},{ing}"),

    ("Give me all forms in order: base form, past tense, past participle, third-person singular present, present participle, of the verb \"{v}\".", "{base},{past},{pp},{s3},{ing}"),
    ("List all forms in order: base form, past tense, past participle, third-person singular present, present participle, of the verb \"{v}\".", "{base},{past},{pp},{s3},{ing}"),

    ("What is the base form of the verb \"{v}\"?", "{base}"),
    ("Return the past tense form for the verb \"{v}\".", "{past}"),
    ("Return the past participle form for the verb \"{v}\".", "{pp}"),
    ("What is the third-person singular present form of \"{v}\" (he/she/it)?", "{s3}"),
    ("Return the present participle form of the verb \"{v}\" (ending with -ing).", "{ing}"),
    ("List the past tense form and the past participle form in this order for the verb \"{v}\".", "{past},{pp}"),
    ("List the third-person singular present form and the present participle form in this order for the verb \"{v}\".", "{s3},{ing}"),

    ("Give me the dictionary form of the verb \"{v}\".", "{base}"),
]


def generate_jsonl(verbs: List[str], out_path: str, irregular: Dict[str, Dict[str, str]]) -> int:
    count = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for v in verbs:
            forms = build_forms(v, irregular)
            for q_tmpl, a_tmpl in TEMPLATES:
                rec = {
                    "context": "",
                    "question": q_tmpl.format(v=v),
                    "answer": a_tmpl.format(**forms),
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1

    print(f"Generated {count} records into {out_path}")
    return count


if __name__ == "__main__":
    # Put your 100 verbs here (base forms)
    verbs_100 = [
        "go", "take", "make", "know", "think", "see", "come", "want", "use", "find",
        # ... add up to 100
    ]

    # Irregular overrides: expand this for your verbs.
    # keys: base verb; values may include past, pp, s3, ing (base optional)
    irregular = {
        "go":   {"past": "went", "pp": "gone", "s3": "goes", "ing": "going"},
        "take": {"past": "took", "pp": "taken"},
        "come": {"past": "came", "pp": "come"},
        "see":  {"past": "saw", "pp": "seen"},
        "make": {"past": "made", "pp": "made"},
        "know": {"past": "knew", "pp": "known"},
        "think":{"past": "thought", "pp": "thought"},
        "find": {"past": "found", "pp": "found"},
        # add more irregulars here...
    }

    generate_jsonl(verbs_100, "verbs_sft.jsonl", irregular)
    print("Wrote:", "verbs_sft.jsonl")
