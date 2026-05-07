def choose_move(observation):
    def ti(v):
        try:
            return int(v)
        except:
            return 0

    w = ti(observation.get("grid_width", 8)) or 8
    h = ti(observation.get("grid_height", 8)) or 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = ti(sp[0]), ti(sp[1])
    ox, oy = ti(op[0]), ti(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        x = y = None
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
        elif isinstance(p, dict) and "x" in p and "y" in p:
            x, y = ti(p.get("x")), ti(p.get("y"))
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        x = y = None
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = ti(r.get("x")), ti(r.get("y"))
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    best_d = None
    best_idx = None

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not res:
        # fallback: deterministic move toward opponent if possible, else stay
        for i, (dx, dy) in enumerate(moves):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                d = manh(nx, ny, ox, oy)
                if best is None or d < best_d or (d == best_d and i < best_idx):
                    best, best_d, best_idx = [dx, dy], d, i
        return best if best is not None else [0, 0]

    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            d = min(manh(nx, ny, rx, ry) for (rx, ry) in res)
            if best is None or d < best_d or (d == best_d and i < best_idx):
                best, best_d, best_idx = [dx, dy], d, i

    return best if best is not None else [0, 0]