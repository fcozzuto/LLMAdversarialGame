def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (W - 1, H - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = (p[0], p[1]) if isinstance(p, (list, tuple)) else (p.get("x", 0), p.get("y", 0))
        except Exception:
            continue
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H:
            obstacles.add((x, y))

    def norm_pos(p):
        try:
            x, y = (p[0], p[1]) if isinstance(p, (list, tuple)) else (p.get("x", 0), p.get("y", 0))
        except Exception:
            return None
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            return x, y
        return None

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    targets = []
    for p in (observation.get("resources") or []):
        tp = norm_pos(p)
        if tp is not None:
            targets.append(tp)
    if not targets:
        for p in (observation.get("unclaimed_cells") or []):
            tp = norm_pos(p)
            if tp is not None:
                targets.append(tp)

    if targets:
        tx, ty = min(targets, key=lambda t: (man(sx, sy, t[0], t[1]), man(ox, oy, t[0], t[1]), t[0], t[1]))
    else:
        tx, ty = W // 2, H // 2

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = (10**9, -10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue
        score_close = -man(nx, ny, tx, ty)
        score_opp = man(nx, ny, ox, oy)
        # Prefer closer to target, then farther from opponent, then deterministic direction order
        key = (man(nx, ny, tx, ty), -score_opp, dx, dy)
        if (key[0], key[1], key[2], key[3]) < (best[0], best[1], best[2], best[3]):
            best = (key[0], key[1], dx, dy)

    return [best[2], best[3]]