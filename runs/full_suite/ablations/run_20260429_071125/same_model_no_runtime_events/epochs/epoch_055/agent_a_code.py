def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    legal = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource that we can plausibly secure (prefer where we are not behind).
    # If resources are empty, move toward center while drifting away from opponent.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we are behind opponent, penalize more when closer distance.
            behind = do - ds
            key = (0 if behind <= 0 else 1, abs(ds), behind, cheb(ox, oy, rx, ry))
            if best is None or key < best_key:
                best, best_key = (rx, ry), key
        tx, ty = best
    else:
        # deterministic fallback: approach center (3.5,3.5) with slight avoidance of opponent
        tx, ty = (w // 2, h // 2)
        # If opponent is very close, shift toward farther corner deterministically
        dpo = cheb(sx, sy, ox, oy)
        if dpo <= 2:
            tx, ty = (0, 0) if (ox + oy) >= (w - 1 + h - 1) // 2 else (w - 1, h - 1)

    # Evaluate moves: prioritize reducing distance to target, then increasing distance to opponent, avoid stepping into obstacles.
    cur_to_t = cheb(sx, sy, tx, ty)
    best_move = legal[0]
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        # Small tie-breakers to reduce oscillation: prefer moves that progress toward target.
        score = (ds, -do, 0 if ds < cur_to_t else 1, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]