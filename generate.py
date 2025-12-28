
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

    verbs_160 = [
        # your original 10
        "go", "take", "make", "know", "think", "see", "come", "want", "use", "find",

        # additional 118
        "get", "give", "tell", "work", "call", "try", "ask", "need", "feel", "become",
        "leave", "put", "mean", "keep", "let", "begin", "seem", "help", "talk", "turn",
        "start", "show", "hear", "play", "run", "move", "like", "live", "believe", "hold",
        "bring", "happen", "write", "provide", "sit", "stand", "lose", "pay", "meet", "include",
        "continue", "set", "learn", "change", "lead", "understand", "watch", "follow", "stop", "create",
        "speak", "read", "allow", "add", "spend", "grow", "open", "walk", "win", "offer",
        "remember", "love", "consider", "appear", "buy", "wait", "serve", "die", "send", "expect",
        "build", "stay", "fall", "cut", "reach", "kill", "remain", "suggest", "raise", "pass",
        "sell", "decide", "return", "explain", "hope", "develop", "carry", "break", "choose", "draw",
        "drive", "eat", "drink", "sleep", "read", "write", "speak", "listen", "hear", "learn",
        "teach", "study", "plan", "travel", "meet", "join", "leave", "arrive", "enter", "finish",
        "close", "answer", "help", "push", "pull", "cook", "clean", "wash", "buy", "sell",
        "send", "receive", "show", "hide", "forget", "forgive", "catch", "throw",

        "be", "say", "wear", "tear", "swim", "sing", "ring", "rise",
        "shake", "shine", "shoot", "shut", "slide", "smell", "swing", "swear",
        "lend", "hit", "hurt", "dig", "feed", "fight", "fly", "freeze",
        "hang", "lay", "lie", "light", "ride", "seek", "stick", "strike",
    ]

    # Irregular overrides: expand this for your verbs.
    # keys: base verb; values may include past, pp, s3, ing (base optional)
    irregular = {
        "go": {"past": "went", "pp": "gone", "s3": "goes", "ing": "going"},
        "take": {"past": "took", "pp": "taken", "s3": "takes", "ing": "taking"},
        "make": {"past": "made", "pp": "made", "s3": "makes", "ing": "making"},
        "know": {"past": "knew", "pp": "known", "s3": "knows", "ing": "knowing"},
        "think": {"past": "thought", "pp": "thought", "s3": "thinks", "ing": "thinking"},
        "see": {"past": "saw", "pp": "seen", "s3": "sees", "ing": "seeing"},
        "come": {"past": "came", "pp": "come", "s3": "comes", "ing": "coming"},
        "want": {"past": "wanted", "pp": "wanted", "s3": "wants", "ing": "wanting"},
        "use": {"past": "used", "pp": "used", "s3": "uses", "ing": "using"},
        "find": {"past": "found", "pp": "found", "s3": "finds", "ing": "finding"},
        "get": {"past": "got", "pp": "gotten", "s3": "gets", "ing": "getting"},
        "give": {"past": "gave", "pp": "given", "s3": "gives", "ing": "giving"},
        "tell": {"past": "told", "pp": "told", "s3": "tells", "ing": "telling"},
        "work": {"past": "worked", "pp": "worked", "s3": "works", "ing": "working"},
        "call": {"past": "called", "pp": "called", "s3": "calls", "ing": "calling"},
        "try": {"past": "tried", "pp": "tried", "s3": "tries", "ing": "trying"},
        "ask": {"past": "asked", "pp": "asked", "s3": "asks", "ing": "asking"},
        "need": {"past": "needed", "pp": "needed", "s3": "needs", "ing": "needing"},
        "feel": {"past": "felt", "pp": "felt", "s3": "feels", "ing": "feeling"},
        "become": {"past": "became", "pp": "become", "s3": "becomes", "ing": "becoming"},
        "leave": {"past": "left", "pp": "left", "s3": "leaves", "ing": "leaving"},
        "put": {"past": "put", "pp": "put", "s3": "puts", "ing": "putting"},
        "mean": {"past": "meant", "pp": "meant", "s3": "means", "ing": "meaning"},
        "keep": {"past": "kept", "pp": "kept", "s3": "keeps", "ing": "keeping"},
        "let": {"past": "let", "pp": "let", "s3": "lets", "ing": "letting"},
        "begin": {"past": "began", "pp": "begun", "s3": "begins", "ing": "beginning"},
        "seem": {"past": "seemed", "pp": "seemed", "s3": "seems", "ing": "seeming"},
        "help": {"past": "helped", "pp": "helped", "s3": "helps", "ing": "helping"},
        "talk": {"past": "talked", "pp": "talked", "s3": "talks", "ing": "talking"},
        "turn": {"past": "turned", "pp": "turned", "s3": "turns", "ing": "turning"},
        "start": {"past": "started", "pp": "started", "s3": "starts", "ing": "starting"},
        "show": {"past": "showed", "pp": "shown", "s3": "shows", "ing": "showing"},
        "hear": {"past": "heard", "pp": "heard", "s3": "hears", "ing": "hearing"},
        "play": {"past": "played", "pp": "played", "s3": "plays", "ing": "playing"},
        "run": {"past": "ran", "pp": "run", "s3": "runs", "ing": "running"},
        "move": {"past": "moved", "pp": "moved", "s3": "moves", "ing": "moving"},
        "like": {"past": "liked", "pp": "liked", "s3": "likes", "ing": "liking"},
        "live": {"past": "lived", "pp": "lived", "s3": "lives", "ing": "living"},
        "believe": {"past": "believed", "pp": "believed", "s3": "believes", "ing": "believing"},
        "hold": {"past": "held", "pp": "held", "s3": "holds", "ing": "holding"},
        "bring": {"past": "brought", "pp": "brought", "s3": "brings", "ing": "bringing"},
        "happen": {"past": "happened", "pp": "happened", "s3": "happens", "ing": "happening"},
        "write": {"past": "wrote", "pp": "written", "s3": "writes", "ing": "writing"},
        "provide": {"past": "provided", "pp": "provided", "s3": "provides", "ing": "providing"},
        "sit": {"past": "sat", "pp": "sat", "s3": "sits", "ing": "sitting"},
        "stand": {"past": "stood", "pp": "stood", "s3": "stands", "ing": "standing"},
        "lose": {"past": "lost", "pp": "lost", "s3": "loses", "ing": "losing"},
        "pay": {"past": "paid", "pp": "paid", "s3": "pays", "ing": "paying"},
        "meet": {"past": "met", "pp": "met", "s3": "meets", "ing": "meeting"},
        "include": {"past": "included", "pp": "included", "s3": "includes", "ing": "including"},
        "continue": {"past": "continued", "pp": "continued", "s3": "continues", "ing": "continuing"},
        "set": {"past": "set", "pp": "set", "s3": "sets", "ing": "setting"},
        "learn": {"past": "learned", "pp": "learned", "s3": "learns", "ing": "learning"},
        "change": {"past": "changed", "pp": "changed", "s3": "changes", "ing": "changing"},
        "lead": {"past": "led", "pp": "led", "s3": "leads", "ing": "leading"},
        "understand": {"past": "understood", "pp": "understood", "s3": "understands", "ing": "understanding"},
        "watch": {"past": "watched", "pp": "watched", "s3": "watches", "ing": "watching"},
        "follow": {"past": "followed", "pp": "followed", "s3": "follows", "ing": "following"},
        "stop": {"past": "stopped", "pp": "stopped", "s3": "stops", "ing": "stopping"},
        "create": {"past": "created", "pp": "created", "s3": "creates", "ing": "creating"},
        "speak": {"past": "spoke", "pp": "spoken", "s3": "speaks", "ing": "speaking"},
        "read": {"past": "read", "pp": "read", "s3": "reads", "ing": "reading"},
        "allow": {"past": "allowed", "pp": "allowed", "s3": "allows", "ing": "allowing"},
        "add": {"past": "added", "pp": "added", "s3": "adds", "ing": "adding"},
        "spend": {"past": "spent", "pp": "spent", "s3": "spends", "ing": "spending"},
        "grow": {"past": "grew", "pp": "grown", "s3": "grows", "ing": "growing"},
        "open": {"past": "opened", "pp": "opened", "s3": "opens", "ing": "opening"},
        "walk": {"past": "walked", "pp": "walked", "s3": "walks", "ing": "walking"},
        "win": {"past": "won", "pp": "won", "s3": "wins", "ing": "winning"},
        "offer": {"past": "offered", "pp": "offered", "s3": "offers", "ing": "offering"},
        "remember": {"past": "remembered", "pp": "remembered", "s3": "remembers", "ing": "remembering"},
        "love": {"past": "loved", "pp": "loved", "s3": "loves", "ing": "loving"},
        "consider": {"past": "considered", "pp": "considered", "s3": "considers", "ing": "considering"},
        "appear": {"past": "appeared", "pp": "appeared", "s3": "appears", "ing": "appearing"},
        "buy": {"past": "bought", "pp": "bought", "s3": "buys", "ing": "buying"},
        "wait": {"past": "waited", "pp": "waited", "s3": "waits", "ing": "waiting"},
        "serve": {"past": "served", "pp": "served", "s3": "serves", "ing": "serving"},
        "die": {"past": "died", "pp": "died", "s3": "dies", "ing": "dying"},
        "send": {"past": "sent", "pp": "sent", "s3": "sends", "ing": "sending"},
        "expect": {"past": "expected", "pp": "expected", "s3": "expects", "ing": "expecting"},
        "build": {"past": "built", "pp": "built", "s3": "builds", "ing": "building"},
        "stay": {"past": "stayed", "pp": "stayed", "s3": "stays", "ing": "staying"},
        "fall": {"past": "fell", "pp": "fallen", "s3": "falls", "ing": "falling"},
        "cut": {"past": "cut", "pp": "cut", "s3": "cuts", "ing": "cutting"},
        "reach": {"past": "reached", "pp": "reached", "s3": "reaches", "ing": "reaching"},
        "kill": {"past": "killed", "pp": "killed", "s3": "kills", "ing": "killing"},
        "remain": {"past": "remained", "pp": "remained", "s3": "remains", "ing": "remaining"},
        "suggest": {"past": "suggested", "pp": "suggested", "s3": "suggests", "ing": "suggesting"},
        "raise": {"past": "raised", "pp": "raised", "s3": "raises", "ing": "raising"},
        "pass": {"past": "passed", "pp": "passed", "s3": "passes", "ing": "passing"},
        "sell": {"past": "sold", "pp": "sold", "s3": "sells", "ing": "selling"},
        "decide": {"past": "decided", "pp": "decided", "s3": "decides", "ing": "deciding"},
        "return": {"past": "returned", "pp": "returned", "s3": "returns", "ing": "returning"},
        "explain": {"past": "explained", "pp": "explained", "s3": "explains", "ing": "explaining"},
        "hope": {"past": "hoped", "pp": "hoped", "s3": "hopes", "ing": "hoping"},
        "develop": {"past": "developed", "pp": "developed", "s3": "develops", "ing": "developing"},
        "carry": {"past": "carried", "pp": "carried", "s3": "carries", "ing": "carrying"},
        "break": {"past": "broke", "pp": "broken", "s3": "breaks", "ing": "breaking"},
        "choose": {"past": "chose", "pp": "chosen", "s3": "chooses", "ing": "choosing"},
        "draw": {"past": "drew", "pp": "drawn", "s3": "draws", "ing": "drawing"},
        "drive": {"past": "drove", "pp": "driven", "s3": "drives", "ing": "driving"},
        "eat": {"past": "ate", "pp": "eaten", "s3": "eats", "ing": "eating"},
        "drink": {"past": "drank", "pp": "drunk", "s3": "drinks", "ing": "drinking"},
        "sleep": {"past": "slept", "pp": "slept", "s3": "sleeps", "ing": "sleeping"},
        "listen": {"past": "listened", "pp": "listened", "s3": "listens", "ing": "listening"},
        "teach": {"past": "taught", "pp": "taught", "s3": "teaches", "ing": "teaching"},
        "study": {"past": "studied", "pp": "studied", "s3": "studies", "ing": "studying"},
        "plan": {"past": "planned", "pp": "planned", "s3": "plans", "ing": "planning"},
        "travel": {"past": "traveled", "pp": "traveled", "s3": "travels", "ing": "traveling"},
        "join": {"past": "joined", "pp": "joined", "s3": "joins", "ing": "joining"},
        "arrive": {"past": "arrived", "pp": "arrived", "s3": "arrives", "ing": "arriving"},
        "enter": {"past": "entered", "pp": "entered", "s3": "enters", "ing": "entering"},
        "finish": {"past": "finished", "pp": "finished", "s3": "finishes", "ing": "finishing"},
        "close": {"past": "closed", "pp": "closed", "s3": "closes", "ing": "closing"},
        "answer": {"past": "answered", "pp": "answered", "s3": "answers", "ing": "answering"},
        "push": {"past": "pushed", "pp": "pushed", "s3": "pushes", "ing": "pushing"},
        "pull": {"past": "pulled", "pp": "pulled", "s3": "pulls", "ing": "pulling"},
        "cook": {"past": "cooked", "pp": "cooked", "s3": "cooks", "ing": "cooking"},
        "clean": {"past": "cleaned", "pp": "cleaned", "s3": "cleans", "ing": "cleaning"},
        "wash": {"past": "washed", "pp": "washed", "s3": "washes", "ing": "washing"},
        "receive": {"past": "received", "pp": "received", "s3": "receives", "ing": "receiving"},
        "hide": {"past": "hid", "pp": "hidden", "s3": "hides", "ing": "hiding"},
        "forget": {"past": "forgot", "pp": "forgotten", "s3": "forgets", "ing": "forgetting"},
        "forgive": {"past": "forgave", "pp": "forgiven", "s3": "forgives", "ing": "forgiving"},
        "catch": {"past": "caught", "pp": "caught", "s3": "catches", "ing": "catching"},
        "throw": {"past": "threw", "pp": "thrown", "s3": "throws", "ing": "throwing"},
        "do": {"past": "did", "pp": "done", "s3": "does", "ing": "doing"},
        "have": {"past": "had", "pp": "had", "s3": "has", "ing": "having"},

        "be":     {"past": "was/were",    "pp": "been",   "s3": "is",     "ing": "being"},   # note: was/were
        "say":    {"past": "said",   "pp": "said",   "s3": "says",   "ing": "saying"},
        "wear":   {"past": "wore",   "pp": "worn",   "s3": "wears",  "ing": "wearing"},
        "tear":   {"past": "tore",   "pp": "torn",   "s3": "tears",  "ing": "tearing"},
        "swim":   {"past": "swam",   "pp": "swum",   "s3": "swims",  "ing": "swimming"},
        "sing":   {"past": "sang",   "pp": "sung",   "s3": "sings",  "ing": "singing"},
        "ring":   {"past": "rang",   "pp": "rung",   "s3": "rings",  "ing": "ringing"},
        "rise":   {"past": "rose",   "pp": "risen",  "s3": "rises",  "ing": "rising"},
        "shake":  {"past": "shook",  "pp": "shaken", "s3": "shakes", "ing": "shaking"},
        "shine":  {"past": "shone",  "pp": "shone",  "s3": "shines", "ing": "shining"},
        "shoot":  {"past": "shot",   "pp": "shot",   "s3": "shoots", "ing": "shooting"},
        "shut":   {"past": "shut",   "pp": "shut",   "s3": "shuts",  "ing": "shutting"},
        "slide":  {"past": "slid",   "pp": "slid",   "s3": "slides", "ing": "sliding"},
        "smell":  {"past": "smelled","pp": "smelt","s3": "smells", "ing": "smelling"},  # alt: smelt
        "swing":  {"past": "swung",  "pp": "swung",  "s3": "swings", "ing": "swinging"},
        "swear":  {"past": "swore",  "pp": "sworn",  "s3": "swears", "ing": "swearing"},
        "lend":   {"past": "lent",   "pp": "lent",   "s3": "lends",  "ing": "lending"},
        "hit":    {"past": "hit",    "pp": "hit",    "s3": "hits",   "ing": "hitting"},
        "hurt":   {"past": "hurt",   "pp": "hurt",   "s3": "hurts",  "ing": "hurting"},
        "dig":    {"past": "dug",    "pp": "dug",    "s3": "digs",   "ing": "digging"},
        "feed":   {"past": "fed",    "pp": "fed",    "s3": "feeds",  "ing": "feeding"},
        "fight":  {"past": "fought", "pp": "fought", "s3": "fights", "ing": "fighting"},
        "fly":    {"past": "flew",   "pp": "flown",  "s3": "flies",  "ing": "flying"},
        "freeze": {"past": "froze",  "pp": "frozen", "s3": "freezes","ing": "freezing"},
        "hang":   {"past": "hung",   "pp": "hung",   "s3": "hangs",  "ing": "hanging"},
        "lay":    {"past": "laid",   "pp": "laid",   "s3": "lays",   "ing": "laying"},
        "lie":    {"past": "lay",    "pp": "lain",   "s3": "lies",   "ing": "lying"},
        "light":  {"past": "lit",    "pp": "lit",    "s3": "lights", "ing": "lighting"},
        "ride":   {"past": "rode",   "pp": "ridden", "s3": "rides",  "ing": "riding"},
        "seek":   {"past": "sought", "pp": "sought", "s3": "seeks",  "ing": "seeking"},
        "stick":  {"past": "stuck",  "pp": "stuck",  "s3": "sticks", "ing": "sticking"},
        "strike": {"past": "struck", "pp": "struck", "s3": "strikes","ing": "striking"}, 
    }


    generate_jsonl(verbs_160, "verbs_sft.jsonl", irregular)
    print("Wrote:", "verbs_sft.jsonl")
