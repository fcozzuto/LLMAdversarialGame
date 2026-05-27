def choose_move(observation):
    o = observation if isinstance(observation, dict) else {}
    def p(v, d=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            try: return int(v[0]), int(v[1])
            except: return d
        if isinstance(v, dict):
            for k in ("position", "pos", "location", "self_position", "opponent_position", "target"):
                if k in v: return p(v[k], d)
        return d
    def pts(v):
        r = []
        if isinstance(v, dict):
            for k in ("items", "positions", "cells", "tiles", "data", "resources"):
                if k in v: r += pts(v[k])
        elif isinstance(v, (list, tuple, set)):
            for x in v:
                if isinstance(x, dict):
                    t = None
                    for k in ("position", "pos", "location", "x"):
                        if k in x:
                            t = p(x.get(k), None)
                            break
                    if t is None and "y" in x and "x" in x:
                        try: t = (int(x["x"]), int(x["y"]))
                        except: t = None
                    if t is not None: r.append(t)
                elif isinstance(x, (list, tuple)) and len(x) >= 2:
                    r.append(p(x, None))
        return [a for a in r if a is not None]
    s = p(o.get("self_position", o.get("position", o.get("pos", (0, 0)))))
    e = p(o.get("opponent_position", o.get("enemy_position", o.get("enemy", s))))
    ws, hs = o.get("grid_width", 0), o.get("grid_height", 0)
    obs = set(tuple(p(x, (-999, -999))) for x in o.get("obstacles", []))
    res = pts(o.get("resources", []))
    best = None; bd = 10**9
    for x, y in res:
        d = abs(x - s[0]) + abs(y - s[1])
        if d < bd:
            bd = d; best = (x, y)
    if best is None:
        best = e
    dx = 0 if best[0] == s[0] else (1 if best[0] > s[0] else -1)
    dy = 0 if best[1] == s[1] else (1 if best[1] > s[1] else -1)
    cand = [(dx, dy), (dx, 0), (0, dy), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    for a, b in cand:
        nx, ny = s[0] + a, s[1] + b
        if (nx, ny) not in obs and (ws <= 0 or 0 <= nx < ws) and (hs <= 0 or 0 <= ny < hs):
            return [a, b]
    return [0, 0]
