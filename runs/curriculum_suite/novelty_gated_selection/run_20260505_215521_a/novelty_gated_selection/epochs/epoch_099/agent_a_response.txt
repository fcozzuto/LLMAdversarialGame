def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not res:
        tx, ty = w // 2, h // 2
    else:
        best_val = None
        best_t = (sx, sy)
        for (tx, ty) in res:
            ds = manh(sx, sy, tx, ty)
            do = manh(ox, oy, tx, ty)
            # Prefer resources we can reach sooner; slightly prefer closer to center if tied
            center_bias = manh(tx, ty, w // 2, h // 2) * 0.001
            val = (ds - do) + center_bias
            if best_val is None or val < best_val or (val == best_val and ds < manh(sx, sy, best_t[0], best_t[1])):
                best_val = val
                best_t = (tx, ty)
        tx, ty = best_t

    # Choose one step that reduces distance to target, avoiding obstacles; if stuck, pick best fallback.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        d = manh(nx, ny, tx, ty)
        # Add mild "keep away from opponent" to break ties deterministically
        opp_d = manh(nx, ny, ox, oy)
        score = d - 0.01 * opp_d
        if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    if best is not None:
        return [int(best[1][0]), int(best[1][1])]

    return [0, 0]