"""writelog.py: the one way the build writes into a fixed binary (arm9 section 0), so romcheck can audit it.

Each write is logged as (offset, bytes it replaces, bytes written, writer); `tools/romcheck.py` feeds the log to
romdiff.check: it then fails on a write whose original bytes differ from the dump, overlapping writes, a write a
later one overwrote, and any changed byte no write explains.
"""


def put(buf, off, data, by, log=None, expect=None):
    """buf[off:off+len(data)] = data, logged. expect: bytes the original must hold there (hook sites)."""
    data = bytes(data)
    old = bytes(buf[off:off + len(data)])
    if expect is not None and old != expect:
        raise ValueError(f"{by} at {off:#x}: expected {expect.hex()}, found {old.hex()}")
    if log is not None:
        log.append((off, old, data, by))
    buf[off:off + len(data)] = data


def dump(logs):
    """Text form of {target: log}: `TARGET OFFSET ORIG_HEX NEW_HEX writer` per line."""
    return "".join(f"{t} {off:X} {old.hex()} {new.hex()} {by}\n"
                   for t, log in sorted(logs.items()) for off, old, new, by in log)


def load(path):
    """{target: [(offset, orig bytes, new bytes, writer)]} from dump()'s text."""
    out = {}
    for line in open(path, encoding="utf-8"):
        p = line.split(None, 4)
        if p:
            out.setdefault(p[0], []).append((int(p[1], 16), bytes.fromhex(p[2]), bytes.fromhex(p[3]),
                                             p[4].strip() if len(p) > 4 else ""))
    return out
