def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Drift towards opening away from opponent while avoiding obstacle adjacency
        def adj_pen(x, y):
            if not blocked: return 0
            pen = 0
            for bx, by in blocked:
                if abs(bx-x) <= 1 and abs(by-y) <= 1:
                    pen += 2
            return pen
        best = None
        for dx, dy, nx, ny in legal:
            v = (cheb(nx, ny, ox, oy), -adj_pen(nx, ny), -dx, -dy)
            if best is None or v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    def nearest_opening_after(x, y):
        # Penalize being in/near a wall cluster by counting how many next cells are free
        cnt = 0
        for ddx, ddy in moves:
            nx, ny = x + ddx, y + ddy
            if ok(nx, ny):
                cnt += 1
        return cnt

    # Evaluate each move by best target resource: prefer (i) our being closer than opp, (ii) maximizing gap,
    # and (iii) not stepping into cramped areas.
    best = None
    for dx, dy, nx, ny in legal:
        open_free = nearest_opening_after(nx, ny)
        # Base encourages moving closer to opponent only if it also helps secure resources.
        local_best = None
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # If we can get there no worse than opponent, this is good; otherwise still consider smallest loss.
            gap = d_op - d_me  # positive means advantage
            # Larger gap dominates; slight preference for shorter our distance to claimed targets.
            score = (gap, -d_me, open_free)
            if local_best is None or score > local_best:
                local_best = score
        # Add a deterministic tie-break: prefer lexicographically smallest move among equals via -dx,-dy
        cand = (local_best[0], local_best[1], local_best[2], -dx, -dy)
        if best is None or cand > best[0]:
            best = (cand, dx, dy)

    return [best[1], best[2]]