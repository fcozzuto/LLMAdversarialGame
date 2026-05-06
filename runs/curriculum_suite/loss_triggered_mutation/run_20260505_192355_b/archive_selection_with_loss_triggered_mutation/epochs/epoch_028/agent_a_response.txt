def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # Choose target resource: prefer ones we can reach before opponent, otherwise deny.
    best = None
    for x, y in res:
        sd = md(sx, sy, x, y)
        od = md(ox, oy, x, y)
        # Make higher score better; tie-break deterministically by coords.
        gain = (od - sd)
        score = (gain * 10) - sd + (1 if sd == 0 else 0)
        key = (-(score), x, y)  # minimize
        if best is None or key < best[0]:
            best = (key, x, y)
    tx, ty = best[1], best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order: already fixed list.
    best_move = (None, None)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue
        nsd = md(nx, ny, tx, ty)
        nod = md(nx, ny, ox, oy)
        # Lower is better: reduce distance to target, keep opponent far, prefer stable progress.
        key = (nsd, -nod, abs(dx) + abs(dy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    if best_move[0] is None:
        return [0, 0]
    return best_move