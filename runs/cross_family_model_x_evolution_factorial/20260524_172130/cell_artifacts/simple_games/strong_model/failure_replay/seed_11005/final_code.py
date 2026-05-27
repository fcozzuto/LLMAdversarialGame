def choose_move(observation):
    o = observation if isinstance(observation, dict) else {}
    w = int(o.get("grid_width", 0) or 0)
    h = int(o.get("grid_height", 0) or 0)
    sp = o.get("self_position", (0, 0))
    op = o.get("opponent_position", (0, 0))
    res = o.get("resources", []) or []
    obs = o.get("obstacles", []) or []
    sx, sy = (sp[0], sp[1]) if isinstance(sp, (list, tuple)) and len(sp) > 1 else (0, 0)
    ox, oy = (op[0], op[1]) if isinstance(op, (list, tuple)) and len(op) > 1 else (0, 0)
    blocked = {(p[0], p[1]) for p in obs if isinstance(p, (list, tuple)) and len(p) > 1}
    best = None
    target = None
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) > 1:
            x, y = p[0], p[1]
            d = abs(x - sx) + abs(y - sy)
            if best is None or d < best or (d == best and (x, y) < target):
                best, target = d, (x, y)
    if target is None:
        target = (ox, oy)
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    cand = [(dx, dy), (dx, 0), (0, dy), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    seen = set()
    for a, b in cand:
        if (a, b) in seen:
            continue
        seen.add((a, b))
        nx, ny = sx + a, sy + b
        if (w <= 0 or 0 <= nx < w) and (h <= 0 or 0 <= ny < h) and (nx, ny) not in blocked:
            return [a, b]
    return [0, 0]
