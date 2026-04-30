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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

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
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -(cheb((nx, ny), (cx, cy))) - 0.1 * cheb((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [int(best[0]), int(best[1])]

    res_list = [(r[0], r[1]) for r in resources if r and len(r) >= 2]
    if not res_list:
        for dx, dy, _, _ in legal:
            return [int(dx), int(dy)]
    # Target selection: prefer resources closer to us, and farther from opponent.
    best_t = None; best_key = None
    for rx, ry in res_list:
        d1 = cheb((sx, sy), (rx, ry))
        d2 = cheb((ox, oy), (rx, ry))
        key = (d1 - d2, d1, -d2, rx, ry)  # maximize our advantage
        if best_key is None or key < best_key:
            best_key = key; best_t = (rx, ry)

    tx, ty = best_t
    # If opponent is adjacent and we aren't, slightly prioritize contesting their closest direction.
    opp_close = cheb((sx, sy), (ox, oy)) <= 1

    best = None; bestv = -10**18
    for dx, dy, nx, ny in legal:
        d_us = cheb((nx, ny), (tx, ty))
        d_t_opp = cheb((ox, oy), (tx, ty))
        # Small reward for reducing opponent's distance to target (discourage letting them grab first).
        v = -d_us + 0.05 * (d_t_opp - cheb((nx, ny), (ox, oy)))
        if opp_close:
            v += 0.15 * (cheb((nx, ny), (ox, oy)) - cheb((sx, sy), (ox, oy)))
        # Tie-break deterministically toward lower dx, then lower dy
        tie = (v, -dx, -dy)
        if best is None or tie > bestv:
            bestv = tie
            best = (dx, dy)

    return [int(best[0]), int(best[1])]