def choose_move(observation):
    o = observation if isinstance(observation, dict) else {}
    w = int(o.get("grid_width", 0) or 0)
    h = int(o.get("grid_height", 0) or 0)

    def p(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            a, b = v[0], v[1]
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                return [int(a), int(b)]
        if isinstance(v, dict):
            for a, b in (("x", "y"), ("col", "row"), ("cx", "cy")):
                if a in v and b in v and isinstance(v[a], (int, float)) and isinstance(v[b], (int, float)):
                    return [int(v[a]), int(v[b])]
        return None

    def pts(v):
        r = []
        q = p(v)
        if q is not None:
            r.append(q)
        if isinstance(v, dict):
            for x in v.values():
                if isinstance(x, (list, tuple, dict)):
                    r += pts(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                if isinstance(x, (list, tuple, dict)):
                    r += pts(x)
        return r

    me = p(o.get("self_position")) or p(o.get("position")) or [0, 0]
    op = p(o.get("opponent_position")) or [w - 1, h - 1]
    res = pts(o.get("resources"))
    obs = {tuple(x) for x in pts(o.get("obstacles"))}
    path = {tuple(x) for x in pts(o.get("self_path"))}

    best, bd = None, 10**9
    for x, y in res:
        d = abs(x - me[0]) + abs(y - me[1])
        if d < bd:
            bd, best = d, [x, y]
    if best is None:
        best = op if (abs(op[0] - me[0]) + abs(op[1] - me[1])) <= 2 else [w // 2, h // 2]

    dx = 0 if best[0] == me[0] else (1 if best[0] > me[0] else -1)
    dy = 0 if best[1] == me[1] else (1 if best[1] > me[1] else -1)

    cand = [(dx, dy), (dx, 0), (0, dy), (dx, -dy if dy else 0), (-dx if dx else 0, dy), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    for a, b in cand:
        nx, ny = me[0] + a, me[1] + b
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and (nx, ny) not in path:
            return [a, b]
    return [0, 0]
