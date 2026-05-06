def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target_score(px, py):
        if not resources:
            d_op = cheb(px, py, ox, oy)
            return (-(d_op), 0, 0)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets where we are closer than opponent (do - ds larger)
            # Tie-break: shorter self distance, then stable coordinate ordering.
            val = (do - ds, -ds, -(rx + 131 * ry))
            if best is None or val > best:
                best = val
        if best is None:
            d_op = cheb(px, py, ox, oy)
            return (-(d_op), 0, 0)
        return best

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        tscore = best_target_score(nx, ny)
        # Additional pressure: don't let opponent get too free a line by staying near them
        opp_close = -cheb(nx, ny, ox, oy)
        score = (tscore, opp_close)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]