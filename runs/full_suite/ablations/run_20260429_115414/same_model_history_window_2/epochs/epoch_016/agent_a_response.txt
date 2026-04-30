def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources or remaining <= 0:
        best = (0, 0); bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, cx, cy) - 0.15 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Pick a target deterministically: minimize (self_dist, opp_dist, rx, ry)
    best_t = None
    best_key = None
    for rx, ry in resources:
        ks = cheb(sx, sy, rx, ry)
        ko = cheb(ox, oy, rx, ry)
        key = (ks, ko, rx, ry)
        if best_key is None or key < best_key:
            best_key = key; best_t = (rx, ry)
    tx, ty = best_t

    # One-step greedy with anti-blocking pressure on opponent
    best = (0, 0); bestv = -10**18
    for dx, dy, nx, ny in legal:
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # If we are closer than opponent, we weight it more; also discourage drifting away from center late.
        lead = (opp_d - self_d)
        v = 0
        v += -self_d * 2.0
        v += 0.4 * lead
        # Keep momentum toward target direction: prefer reducing distance compared to staying
        stay_d = cheb(sx, sy, tx, ty)
        v += 0.8 * (stay_d - self_d)
        # Avoid moving into dead-end closeness to opponent (could give them same target line)
        v += -0.12 * cheb(nx, ny, ox, oy)
        # Slight bias to center if distances tie
        v += -0.03 * cheb(nx, ny, cx, cy)

        if v > bestv:
            bestv = v; best = (dx, dy)

    return [int(best[0]), int(best[1])]