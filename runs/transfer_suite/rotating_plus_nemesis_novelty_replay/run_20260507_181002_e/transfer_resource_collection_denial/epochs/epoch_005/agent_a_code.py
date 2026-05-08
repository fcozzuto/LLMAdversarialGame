def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        nx, ny = sx, sy
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a single target resource: closest to us, tie-breaker by closeness to opponent (more dangerous first)
    tx, ty = resources[0]
    best = (10**9, 10**9)
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        key = (d1, -d2)
        if key < best:
            best = key
            tx, ty = rx, ry

    best_move = [0, 0]
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        on_res = 1 if (nx, ny) in set((r[0], r[1]) for r in resources if r is not None and len(r) >= 2) else 0
        margin = (d_opp - d_self)  # positive if we get closer than opponent to target
        score = margin * 3 - d_self + on_res * 50
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move