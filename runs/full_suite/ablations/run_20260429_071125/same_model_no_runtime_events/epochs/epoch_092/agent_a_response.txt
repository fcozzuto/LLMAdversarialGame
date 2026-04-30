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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Strategic shift: pick a move that maximizes "reach advantage" over opponent to the best contested resource.
    best = None
    best_score = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue
        if not resources:
            # If no resources visible, drift toward center while keeping safe.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dist = cheb(nx, ny, int(cx + 0.5), int(cy + 0.5))
            sc = -dist
        else:
            sc = -10**18
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # Higher is better: larger gap in our favor; tie-breaker pushes toward nearer targets.
                val = (d_op - d_me) * 100 - d_me
                if val > sc:
                    sc = val
        # Deterministic tie-break: smaller distance to the same "best-likely" contested area, then lexicographic move.
        if best_score < sc:
            best_score = sc
            best = (dxm, dym)
        elif best_score == sc and best is not None:
            if (dxm, dym) < best:
                best = (dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]