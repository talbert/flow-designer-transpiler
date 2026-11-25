"""Re-identify a flow or action payload: new sys_ids and UUIDs everywhere, including inside the base64-gzip blobs, plus text replacements. Local files only."""
import re, gzip, base64
from fdgen import gid, uid
HEX, UU = r"\b[0-9a-f]{32}\b", r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"
BLOB = r"(<(?:values|trigger_inputs|subflow_inputs)>)([A-Za-z0-9+/=]+)(</)"
def decode(b): return gzip.decompress(base64.b64decode(b)).decode()
def encode(s): return base64.b64encode(gzip.compress(s.encode(), mtime=0)).decode()
def reident(payload, keep, text=None, mapping=None):
    """keep: ids that must not change (platform ids, app id, records that already exist on the target). Returns (new payload, mapping)."""
    mp = dict(mapping or {})
    plain = re.sub(BLOB, lambda m: m.group(1) + decode(m.group(2)) + m.group(3) if False else m.group(0), payload)
    found = set(re.findall(HEX, payload)) | set(re.findall(UU, payload))
    for m in re.finditer(BLOB, payload):
        d = decode(m.group(2)); found |= set(re.findall(HEX, d)) | set(re.findall(UU, d))
    for x in sorted(found):
        if x in keep or x in mp: continue
        mp[x] = uid() if "-" in x else gid()
    def sub(s):
        s = re.sub(UU + "|" + HEX, lambda m: mp.get(m.group(0), m.group(0)), s)
        for a, b in (text or {}).items(): s = s.replace(a, b)
        return s
    out = re.sub(BLOB, lambda m: m.group(1) + encode(sub(decode(m.group(2)))) + m.group(3), payload)
    # outside blobs
    parts = re.split(BLOB, out); res = []
    i = 0
    while i < len(parts):
        res.append(sub(parts[i]))
        if i + 3 < len(parts) + 1 and i + 1 < len(parts): res += [parts[i + 1], parts[i + 2], parts[i + 3]]
        i += 4
    return "".join(res), mp
