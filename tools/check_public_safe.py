#!/usr/bin/env python3
"""Refuse content that should not be in a public repository.

Runs on every commit (local hook) and every push (GitHub Action).
It works by allowlist: anything that names a ServiceNow instance, an email
domain, an application scope or a work item that is not on the short lists
below is reported. Compressed payloads (gzip + base64, the form Flow Designer
stores step values in) are decoded and checked too.

Private terms: if a file named .guard-private-terms exists (it is ignored by
git and never published), each non-empty line in it is an extra forbidden
string, matched without regard to case. Keep employer- or customer-specific
names there, not in this file.

Usage: python3 tools/check_public_safe.py [paths...]   (default: tracked files)
Exit status 1 when anything is found.

Limits. This check knows patterns, not meaning. It cannot know the name of your
employer, your colleagues or your internal systems unless you list them in
.guard-private-terms, and that file exists only on your machine, so the GitHub
Action runs without it. The Action also runs after a push. The local hook is the
real gate: turn it on, keep the private term list filled, and still read what
you commit.
"""
import base64, gzip, os, re, subprocess, sys

ALLOW_HOSTS = {                      # personal developer instances and placeholders
    "dev435256", "dev203052", "dev391418",
    "instance", "yourinstance", "your-instance", "myinstance", "example", "host",
    "developer", "docs", "www", "store", "support", "nowlearning", "signon",
}
ALLOW_EMAIL_DOMAINS = {"example.com", "example.org", "users.noreply.github.com", "anthropic.com"}
ALLOW_EMAILS = {"1234567890@txt.att.net"}          # a made-up SMS gateway address used as sample data
ALLOW_USERS = {"admin", "system", "guest", "maint", "glide.maint", "itil", "abel.tuter", "beth.anglin",
               "tt20.user", "tt20b.user", "{{creator}}", "{{creator_id}}"}
ALLOW_U_NAMES = {"u_table", "u_app_id"}             # inputs of actions that ServiceNow ships
ALLOW_SCOPE_CODES = {"snc", "sn", "906694", "1234", "acme", "abc", "mycompany", "company"}
WORK_ITEMS = r"(?i)(?<![A-Za-z0-9])(?:STRY|STSK|DMND|ENHC|DFCT|PRJTASK|PRJ|EPIC|RLSE|IDEA|CS)\d{6,}(?![0-9])"

RULES = [
    ("instance host", re.compile(r"\b([a-z0-9][a-z0-9-]{1,40})\.(?:service-now\.com|servicenowservices\.com)", re.I),
        lambda m: m.group(1).lower() not in ALLOW_HOSTS),
    ("instance name", re.compile(r"(?im)(?:(?:^|\s)instance=|\"(?:alias|instance)\"\s*:\s*\"|\"-a\"\s*,\s*\")([a-z0-9][a-z0-9_-]{2,40})"),
        lambda m: m.group(1).lower() not in ALLOW_HOSTS | {"pdi435256", "pdi203052", "alias"}
                  and not re.fullmatch(r"[0-9a-f]{32}", m.group(1).lower())),
    ("email address", re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})\b"),
        lambda m: m.group(1).lower() not in ALLOW_EMAIL_DOMAINS and m.group(0).lower() not in ALLOW_EMAILS
                  and not m.group(1).lower().endswith((".png", ".jpg", ".svg", ".js", ".ts", ".md"))),
    ("user name", re.compile(r"(?i)(?:<sys_(?:created|updated)_by>|\"sys_(?:created|updated)_by\"\s*:\s*\"|<user_name>|\"user_name\"\s*:\s*\")([^<\"]{1,60})"),
        lambda m: m.group(1).strip().lower() not in ALLOW_USERS and "{{" not in m.group(1) and "no_such_user" not in m.group(1)),
    ("custom field or table", re.compile(r"(?<![A-Za-z0-9_])(u_[a-z0-9_]{2,40})"),
        lambda m: m.group(1).lower() not in ALLOW_U_NAMES),
    ("government domain", re.compile(r"\b[a-z0-9-]+\.gov\b", re.I), lambda m: True),
    ("work item number", re.compile(WORK_ITEMS), lambda m: True),
    ("custom application scope", re.compile(r"\bx_([a-z0-9]{2,12})_[a-z0-9_]+", re.I),
        lambda m: m.group(1).lower() not in ALLOW_SCOPE_CODES),
    ("credential", re.compile(r"(?i)authorization['\"]?\s*[:=]\s*['\"]?(?:basic|bearer)\s+[A-Za-z0-9+/=._-]{16,}"), lambda m: True),
    ("credential", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), lambda m: True),
    ("credential", re.compile(r"(?i)<(?:password|passwd|secret|token|client_secret|api_key)>\s*[^<\s{][^<]{5,}</"), lambda m: True),
    ("credential", re.compile(r"(?i)\"(?:token|access_token|refresh_token|client_secret|api_key|apikey)\"\s*:\s*\"(?!\{\{|<)[^\"\s]{12,}\""), lambda m: True),
    ("credential", re.compile(r"(?i)\b(?:JSESSIONID|glide_session_store|glide_user_route|BIGipServer[a-z_]*)=[A-Za-z0-9._-]{12,}"), lambda m: True),
    ("credential", re.compile(r"(?i)\b(?:x-usertoken|sysparm_ck)\b['\"]?\s*[:=]\s*['\"]?[0-9a-f]{32,}"), lambda m: True),
    ("credential", re.compile(r"\bcurl\b[^\n]*\s(?:-u|--user)\s+['\"]?[^\s'\":]+:[^\s'\"]{4,}"), lambda m: True),
    ("credential", re.compile(r"(?i)\b(?:password|passwd)\s*[:=]\s*(?!\{\{|<|\$|your|xxx|\*|password|changeme|string|true|false|null|none)[^\s'\",;]{8,}"),
        lambda m: "password2" not in m.group(0).lower()),
    ("credential", re.compile(r"\b(?:ghp|gho|github_pat)_[A-Za-z0-9_]{20,}\b"), lambda m: True),
    ("credential", re.compile(r"(?i)\b(?:g_ck|x-usertoken)\b['\"]?\s*[:=]\s*['\"][0-9a-f]{32,}"), lambda m: True),
    ("credential", re.compile(r"(?i)\b(?:password|passwd|client_secret|api_key)\b['\"]?\s*[:=]\s*['\"](?!\{\{|<|\$|your|xxx|\*\*\*|password|changeme)[^'\"\s]{8,}['\"]"), lambda m: True),
    ("home directory path", re.compile(r"(?:/(?:Users|home)/[A-Za-z0-9._-]+|[A-Za-z]:\\\\Users\\\\[A-Za-z0-9._-]+)[^\s\"'`)<]{0,80}"), lambda m: True),
]
WARN_ONLY = set()   # everything found stops the commit
SKIP_FILES = {"LICENSE", "tools/check_public_safe.py"}
B64 = re.compile(r"H4sI[A-Za-z0-9+/]{40,}={0,2}")


def private_terms():
    try:
        return [l.strip().lower() for l in open(".guard-private-terms", encoding="utf-8") if l.strip() and not l.startswith("#")]
    except OSError:
        return []


UNREADABLE = []


def decoded_layers(text, depth=0, where=""):
    """Yield (depth, text) for the text and everything gzip+base64 inside it."""
    yield depth, text
    if depth >= 4:
        return
    good, bad = [], []
    variants = [text, text.replace("\\/", "/"), re.sub(r"(?<=[A-Za-z0-9+/])\s*\n\s*(?=[A-Za-z0-9+/=])", "", text)]
    for variant in variants:
        for m in B64.finditer(variant):
            blob = m.group(0)
            if blob in good or blob in bad:
                continue
            try:
                inner = gzip.decompress(base64.b64decode(blob + "=" * (-len(blob) % 4))).decode("utf-8", "replace")
            except Exception:
                bad.append(blob)
                continue
            good.append(blob)
            yield from decoded_layers(inner, depth + 1, where)
    # a value that failed in one form but was read in another form is not a gap
    if any(not any(g.startswith(b[:40]) for g in good) for b in bad):
        UNREADABLE.append(where)


def scan(path, terms):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    out = []
    for depth, layer in decoded_layers(text, 0, path):
        where = path if depth == 0 else f"{path} (decoded payload, depth {depth})"
        for name, rx, bad in RULES:
            for m in rx.finditer(layer):
                if bad(m):
                    shown = m.group(0) if name != "credential" else m.group(0)[:18] + "…"
                    out.append((name, where, shown[:90]))
        low = layer.lower()
        for t in terms:
            if t in low:
                out.append(("private term", where, "(a term from .guard-private-terms)"))
    return out


def main(argv):
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if top:
        argv = [os.path.abspath(a) for a in argv]
        os.chdir(top)
        argv = [os.path.relpath(a, top) for a in argv]
    files = [f for f in (argv or subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split("\n")) if f]
    terms = private_terms()
    found = []
    for f in files:
        if f and f not in SKIP_FILES and os.path.isfile(f):
            found += scan(f, terms)
    errors = sorted({x for x in found if x[0] not in WARN_ONLY})
    warns = sorted({x for x in found if x[0] in WARN_ONLY})
    for name, where, shown in warns:
        print(f"warning  {name}: {where}: {shown}")
    for name, where, shown in errors:
        print(f"BLOCKED  {name}: {where}: {shown}")
    for where in sorted(set(UNREADABLE)):
        print(f"warning  a compressed value in {where} could not be decoded, so it was not checked")
    print(f"{len(files)} files checked, {len(errors)} blocked, {len(warns)} warnings, "
          f"{'private term list in use' if terms else 'no private term list'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
