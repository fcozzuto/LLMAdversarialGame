def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    if (sx, sy) in obst or not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_t = None
    best_key = None
    for tx, ty in res:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        key = (od - sd) * 1000 - sd  # dominate by relative advantage
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    best_move = (0, 0)
    best_score = None
    for dx in (-1, 0, 1):
        nx = sx + dx
        if not (0 <= nx < w):
            continue
        for dy in (-1, 0, 1):
            ny = sy + dy
            if not (0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue
            # Prefer reducing our distance to target; lightly discourage moving away.
            score = -man(nx, ny, tx, ty)
            # If tie, prefer moves that also increase our advantage vs opponent.
            score2 = (man(ox, oy, tx, ty) - man(nx, ny, tx, ty))
            if best_score is None or (score, score2) > best_score:
                best_score = (score, score2)
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]