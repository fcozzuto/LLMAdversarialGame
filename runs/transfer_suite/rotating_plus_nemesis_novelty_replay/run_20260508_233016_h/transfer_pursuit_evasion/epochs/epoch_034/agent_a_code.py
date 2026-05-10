def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if not (dx == 0 and dy == 0) and legal(sx + dx, sy + dy):
                moves.append((dx, dy))
    if not moves and legal(sx, sy):
        return [0, 0]
    if not moves:
        # try staying put if it's legal
        return [0, 0] if legal(sx, sy) else [0, 0]

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # If opponent is adjacent/near, prioritize moving away; otherwise move toward nearest resource.
    d_opp = dist2(sx, sy, ox, oy)
    away = d_opp <= 2

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if away:
            score = dist2(nx, ny, ox, oy)  # maximize distance
        else:
            if res:
                score = -min(dist2(nx, ny, rx, ry) for rx, ry in res)  # maximize negative distance = minimize distance
            else:
                score = -dist2(nx, ny, ox, oy)  # fallback: move away from opponent slightly
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score
        elif score == best_score:
            # deterministic tie-break: prefer smallest abs dx then abs dy then specific order
            bx, by = best
            if (abs(dx), abs(dy), dx, dy) < (abs(bx), abs(by), bx, by):
                best = (dx, dy)

    return [best[0], best[1]] if best else [0, 0]