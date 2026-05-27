def choose_move(observation):
    o = observation if isinstance(observation, dict) else {}
    w = o.get("grid_width", 0) or 0
    h = o.get("grid_height", 0) or 0

    def pos(v):
        if isinstance(v, dict):
            for k in ("pos", "position", "location", "loc", "xy", "coord"):
                p = v.get(k)
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    return [int(p[0]), int(p[1])]
        if isinstance(v, (list, tuple)) and len(v) >= 2 and not isinstance(v[0], (list, tuple, dict)):
            return [int(v[0]), int(v[1])]
        return None

    me = pos(o.get("self_position")) or pos(o.get("self")) or [0, 0]
    op = pos(o.get("opponent_position")) or pos(o.get("opponent")) or [w - 1, h - 1]

    def items(v):
        out = []
        if isinstance(v, dict):
            p = pos(v)
            if p is not None: out.append(p)
            for x in v.values(): out += items(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                p = pos(x)
                if p is not None: out.append(p)
                else: out += items(x)
        return out

    res = items(o.get("resources"))
    obs = {tuple(p) for p in items(o.get("obstacles"))}
    best = None
    bestd = 10**9

    if res:
        for x, y in res:
            d = abs(x - me[0]) + abs(y - me[1])
            if d < bestd:
                bestd = d
                best = [x, y]
    else:
        best = [w // 2, h // 2] if w and h else [me[0] + (1 if me[0] <= op[0] else -1), me[1] + (1 if me[1] <= op[1] else -1)]

    dx = 0 if best[0] == me[0] else (1 if best[0] > me[0] else -1)
    dy = 0 if best[1] == me[1] else (1 if best[1] > me[1] else -1)
    cand = [(dx, 0), (0, dy), (dx, dy), (-dx, 0), (0, -dy), (0, 0)]

    for a, b in cand:
        nx, ny = me[0] + a, me[1] + b
        if (nx, ny) not in obs and (w == 0 or (0 <= nx < w and 0 <= ny < h)):
            return [a, b]
    return [0, 0]
