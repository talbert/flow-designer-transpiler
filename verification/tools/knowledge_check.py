"""Checks that a rewritten prompt keeps every technical token of the source prompt.
Usage: python3 knowledge_check.py <source.md> <rewritten.md> [--list]
Tokens: 32-hex sys_ids; UUID-free backticked identifiers (tables, fields, pills, values); JSON key names; evidence tags; XML element names."""
import re, sys, pathlib
a = pathlib.Path(sys.argv[1]).read_text(); b = pathlib.Path(sys.argv[2]).read_text()
def toks(t):
    T = {}
    T["sys_id"] = set(re.findall(r"\b[0-9a-f]{32}\b", t))
    bt = set(re.findall(r"`([^`\n]{2,80})`", t))
    T["backticked"] = {x for x in bt if not re.search(r"\{\{[A-Z_]+\}\}", x) or True}
    T["json_key"] = set(re.findall(r'\\?"([A-Za-z_$][A-Za-z0-9_$.]{1,40})\\?"\s*:', t))
    T["xml_element"] = set(re.findall(r"<([a-z][a-z0-9_]{2,60})[ />]", t))
    T["tag"] = set(re.findall(r"`\[([A-Z_]{4,30})\]`", t))
    T["table_like"] = set(re.findall(r"\b((?:sys|sc|var|cmn|sysevent|sysapproval|item|incident)_[a-z0-9_]{3,60})\b", t))
    return T
A, B = toks(a), toks(b); bad = 0
for k in A:
    miss = sorted(A[k] - B[k])
    if k == "backticked": miss = [m for m in miss if m not in b]      # allow the same text outside backticks
    bad += len(miss)
    print(f"{k:12} source {len(A[k]):5}  kept {len(A[k]) - len(miss):5}  missing {len(miss):4}")
    if "--list" in sys.argv:
        for m in miss[:400]: print("    -", m[:120])
print("chars:", len(a), "->", len(b), "| lines:", a.count("\n"), "->", b.count("\n"), "| TOTAL MISSING:", bad)
sys.exit(1 if bad else 0)
