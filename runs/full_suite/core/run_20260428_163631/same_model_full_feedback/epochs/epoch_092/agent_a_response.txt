def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    obstacles.discard((sx, sy))
    obstacles.discard((ox, oy))

    resources = []
    res_set = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    if (sx, sy) in res_set:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        # Try axis-first (deterministic) then diagonals
        cands = []
        cands.append([1 if tx > sx else -1 if tx < sx else 0, 0])
        cands.append([0, 1 if ty > sy else -1 if ty < sy else 0])
        cands.append([dx, dy])
        cands.append([cands[0][0], cands[1][1]])
        cands.append([0, 0])
        for ddx, ddy in cands:
            nx, ny = sx + ddx, sy + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [int(ddx), int(ddy)]
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return move_towards(tx, ty)

    # Prefer resources where we are closer than opponent; break ties deterministically.
    best = None
    best_score = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # Larger advantage first; then our distance; then coordinates
        key = (adv, -sd, -(rx * 100 + ry))
        if best_score is None or key > best_score:
            best_score = key
            best = (rx, ry)

    return move_towards(best[0], best[1])