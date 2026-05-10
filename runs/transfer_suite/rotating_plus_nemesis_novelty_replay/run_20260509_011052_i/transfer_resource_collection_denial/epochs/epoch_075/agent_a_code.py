def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_target(rx, ry):
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # If we can arrive no later than opponent, prioritize that margin; else minimize our time.
        if adv >= 0:
            return (2 * adv + 0.01 * (od + sd), -sd, -od, -(rx + ry), -rx, -ry)
        return (0, - (sd), sd, -od, -(rx + ry), -rx, -ry)

    # Deterministic pick: best score_target
    best = None
    best_key = None
    for rx, ry in resources:
        k = score_target(rx, ry)
        if best_key is None or k > best_key:
            best_key = k
            best = (rx, ry)

    tx, ty = best

    # Choose a legal one-step move minimizing distance to target; break ties by maximizing distance from opponent.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                d1 = cheb(nx, ny, tx, ty)
                d2 = cheb(nx, ny, ox, oy)
                # Deterministic tie-break order: prefer diagonals then right then up then stay.
                diag = 1 if dx != 0 and dy != 0 else 0
                candidates.append(((d1, -d2, -diag, -dx, -dy, dx == 0 and dy == 0), [dx, dy]))

    candidates.sort(reverse=False, key=lambda z: z[0])
    best_move = candidates[0][1] if candidates else [0, 0]
    return [int(best_move[0]), int(best_move[1])]