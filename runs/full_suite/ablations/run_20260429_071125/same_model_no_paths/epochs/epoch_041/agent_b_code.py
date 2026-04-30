def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = None
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        if resources:
            score = 0
            for rx, ry in resources:
                d_my = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                adv = d_op - d_my  # positive if we're closer this turn
                # Strongly prefer targets where we have the lead; tie-break with urgency
                score += (adv * 100) - (d_my * 2)
                # If we're already on a resource tile, dominate
                if nx == rx and ny == ry:
                    score += 10**9
            # If mostly losing everywhere, still gravitate to nearest resource to create future advantage
            nearest = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            score -= nearest * 5
        else:
            nearest = cheb(nx, ny, cx, cy)
            score = -(nearest * 3)
        # Small deterministic tie-break: prefer staying still only when equal
        if best is None or score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]