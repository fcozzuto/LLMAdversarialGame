def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if res:
        best = None
        best_score = None
        for tx, ty in res:
            myd = manh(sx, sy, tx, ty)
            opd = manh(ox, oy, tx, ty)
            # Prefer resources where we are relatively closer than opponent; break ties by absolute closeness.
            score = (opd - myd) * 1000 - myd
            if best is None or score > best_score:
                best_score = score
                best = (tx, ty)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    cur_dist = manh(sx, sy, tx, ty)
    best_move = (0, 0)
    best_md = None
    best_tiebreak = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d = manh(nx, ny, tx, ty)
        if best_md is None or d < best_md:
            best_md = d
            best_move = (dx, dy)
            best_tiebreak = (d - cur_dist, -abs(ox - nx) - abs(oy - ny))
        elif d == best_md:
            tb = (d - cur_dist, -abs(ox - nx) - abs(oy - ny))
            if tb > best_tiebreak:
                best_move = (dx, dy)
                best_tiebreak = tb

    return [best_move[0], best_move[1]]