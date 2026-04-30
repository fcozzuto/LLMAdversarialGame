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

    if not resources or remaining <= 0:
        tx, ty = (ox, oy)  # deterministic endgame: approach opponent corner-ish
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_res = None; bestv = -10**18
    for rx, ry in resources:
        ourd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        # Prefer resources we are closer to; small center bias to reduce deadlocks.
        v = (oppd - ourd) - 0.001 * cheb(rx, ry, cx, cy)
        if v > bestv:
            bestv = v; best_res = (rx, ry)

    tx, ty = best_res
    curd = cheb(sx, sy, tx, ty)
    best = None; bestv = -10**18
    for dx, dy, nx, ny in legal:
        nd = cheb(nx, ny, tx, ty)
        step_gain = curd - nd  # positive means getting closer
        # If multiple equal gains, prefer moves that increase opponent's distance to target indirectly
        # by staying away from opponent (keeps our route less contested).
        opp_dist = cheb(nx, ny, ox, oy)
        v = 10 * step_gain + 0.01 * opp_dist - 0.0001 * cheb(nx, ny, tx, ty)
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]