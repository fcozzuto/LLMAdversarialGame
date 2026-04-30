def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose target resource where we are relatively closer than opponent.
    if resources:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Bias: strongly prefer winning the race to the resource, with small tie-break by absolute distance.
            score = (myd - opd * 0.95, myd, rx, ry)
            if best is None or score < best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
    else:
        # Fallback: head to opponent side center-ish deterministically.
        tx, ty = (7 if ox < w // 2 else 0, 7 if oy < h // 2 else 0)

    # Greedy step toward target, but also consider blocking/denying: prefer moves that reduce our distance more than opponent's.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd_new = cheb(nx, ny, tx, ty)
        opd_new = cheb(ox, oy, tx, ty)
        # If we are already effectively on top, try to move closer to opponent to contest the next resource.
        opp_close = cheb(nx, ny, ox, oy)
        val = (myd_new - opd_new * 0.95, myd_new, opp_close, dx == 0 and dy == 0, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]