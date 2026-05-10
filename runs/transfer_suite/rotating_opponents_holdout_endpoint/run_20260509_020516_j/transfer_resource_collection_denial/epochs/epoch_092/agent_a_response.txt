def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def mdist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_cell, best_key = None, None
    for cx, cy in resources:
        sd = mdist(sx, sy, cx, cy)
        od = mdist(ox, oy, cx, cy)
        key = (od - sd, -sd, -cx, cy)  # maximize race advantage, then closer, deterministic tie-break
        if best_key is None or key > best_key:
            best_key, best_cell = key, (cx, cy)

    tx, ty = best_cell

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = (10**9, -10**9, 0, 0)
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = mdist(nx, ny, tx, ty)
        nod = mdist(nx, ny, ox, oy)
        # Prefer stepping closer to target; if tie, drift away from opponent a bit to reduce denial
        cand = (nsd, nod, -dx, -dy)
        if (cand[0], cand[1], cand[2], cand[3]) < (best[0], best[1], best[2], best[3]):
            best = (nsd, nod, -dx, -dy)
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]