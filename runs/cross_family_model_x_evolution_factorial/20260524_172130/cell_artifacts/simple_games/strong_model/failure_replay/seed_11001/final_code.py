def choose_move(observation):
    g = observation if isinstance(observation, dict) else {}
    w = int(g.get("grid_width", g.get("width", 0)) or 0)
    h = int(g.get("grid_height", g.get("height", 0)) or 0)

    def pos(v):
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                try:
                    return int(v["x"]), int(v["y"])
                except:
                    return None
            for k in ("position", "pos", "location", "loc", "cell", "target"):
                if k in v:
                    p = pos(v[k])
                    if p is not None:
                        return p
        elif isinstance(v, (list, tuple)) and len(v) >= 2 and not isinstance(v[0], (list, tuple, dict)):
            try:
                return int(v[0]), int(v[1])
            except:
                return None
        return None

    def items(v):
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                p = pos(v)
                return [p] if p is not None else []
            out = []
            for x in v.values():
                out += items(x)
            return out
        if isinstance(v, (list, tuple)):
            if len(v) >= 2 and not isinstance(v[0], (list, tuple, dict)):
                p = pos(v)
                return [p] if p is not None else []
            out = []
            for x in v:
                out += items(x)
            return out
        p = pos(v)
        return [p] if p is not None else []

    me = pos(g.get("self_position")) or pos(g.get("self")) or pos(g.get("agent")) or (0, 0)
    opp = pos(g.get("opponent_position")) or pos(g.get("opponent")) or pos(g.get("enemy"))
    res = items(g.get("resources"))
    obs = set(items(g.get("obstacles")))
    path = set(items(g.get("self_path")))

    def score(p):
        return abs(p[0] - me[0]) + abs(p[1] - me[1])

    def step_toward(t):
        dx = 0 if t[0] == me[0] else (1 if t[0] > me[0] else -1)
        dy = 0 if t[1] == me[1] else (1 if t[1] > me[1] else -1)
        cand = [(dx, 0), (0, dy), (dx, dy), (-dx, 0), (0, -dy)]
        for a, b in cand:
            nx, ny = me[0] + a, me[1] + b
            if (a or b) and (w <= 0 or 0 <= nx < w) and (h <= 0 or 0 <= ny < h) and (nx, ny) not in obs and (nx, ny) not in path:
                return [a, b]
        return [0, 0]

    if res:
        best = min(res, key=score)
        mv = step_toward(best)
        if mv != [0, 0]:
            return mv

    if opp is not None:
        dx = 1 if opp[0] > me[0] else (-1 if opp[0] < me[0] else 0)
        dy = 1 if opp[1] > me[1] else (-1 if opp[1] < me[1] else 0)
        for a, b in ((dx, dy), (dx, 0), (0, dy), (-dx, -dy), (dx, -dy), (-dx, dy)):
            nx, ny = me[0] + a, me[1] + b
            if (a or b) and (w <= 0 or 0 <= nx < w) and (h <= 0 or 0 <= ny < h) and (nx, ny) not in obs:
                return [a, b]

    for a, b in ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)):
        nx, ny = me[0] + a, me[1] + b
        if (a or b) and (w <= 0 or 0 <= nx < w) and (h <= 0 or 0 <= ny < h) and (nx, ny) not in obs:
            return [a, b]
    return [0, 0]
