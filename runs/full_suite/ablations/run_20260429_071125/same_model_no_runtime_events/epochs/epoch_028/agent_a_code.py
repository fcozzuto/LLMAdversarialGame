def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best_s = -10**18
        best = resources[0]
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            rel = do - ds  # positive means we are closer
            # Prefer resources we can beat; otherwise, minimize their lead while also being closer.
            s = rel * 30 - ds * 2 - cheb(rx, ry, sx, sy) * 0
            if s > best_s:
                best_s = s
                best = (rx, ry)
        return best

    tx, ty = best_target()

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        # Use opponent distance as a tiebreaker to avoid stepping into their immediate influence.
        do2 = cheb(ox, oy, tx, ty)
        opp_dist = cheb(nx, ny, ox, oy)
        v = (do2 - ds2) * 30 - ds2 * 2 + opp_dist * 0.5
        if v > best_v:
            best_v = v
            best_m = (dx, dy)

    # If all moves blocked, stay.
    return [int(best_m[0]), int(best_m[1])]