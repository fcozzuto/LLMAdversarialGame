def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    cur = set()
    for r in resources:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                cur.add((x, y))
    if not cur:
        return [0, 0]

    # Choose target with best "we are ahead" margin; tie-breaker: smaller self distance.
    best_r = None
    best_margin = None
    best_self_d = None
    for rx, ry in cur:
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        margin = opp_d - self_d
        if best_r is None or margin > best_margin or (margin == best_margin and self_d < best_self_d):
            best_r = (rx, ry)
            best_margin = margin
            best_self_d = self_d

    rx, ry = best_r

    # One-step lookahead: pick move that maximizes post-move margin for same target.
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            self_d2 = cheb(nx, ny, rx, ry)
            opp_d2 = cheb(ox, oy, rx, ry)
            margin2 = opp_d2 - self_d2
            score = margin2 * 10 - self_d2
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    # If all moves invalid (e.g., surrounded by obstacles), stay.
    return best_move if best_move is not None else [0, 0]