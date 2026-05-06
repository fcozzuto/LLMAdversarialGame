def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh_obs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]

    # Predict opponent target as its nearest resource (Chebyshev)
    tx, ty = min(resources, key=lambda r: cheb(ox, oy, r[0], r[1]))

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    def obstacle_prox(nx, ny):
        p = 0
        for dx, dy in neigh_obs:
            ax, ay = nx + dx, ny + dy
            if in_bounds(ax, ay) and (ax, ay) in obstacles:
                p += 1
        return p

    def opp_best_dist_after():
        best = 10**9
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best:
                best = d
        return best if best != 10**9 else cheb(ox, oy, tx, ty)

    opp_dist_after = opp_best_dist_after()

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_dist = cheb(nx, ny, tx, ty)
        # Encourage getting closer than opponent can, penalize obstacle tightness
        score = (opp_dist_after - self_dist) * 100 - obstacle_prox(nx, ny) * 3
        # Tie-break deterministically by closer to center, then by move
        cx = (w - 1) * 0.5
        cy = (h - 1) * 0.5
        score -= int((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]