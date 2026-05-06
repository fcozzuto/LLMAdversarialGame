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

    valid_resources = [(rx, ry) for (rx, ry) in resources if (rx, ry) not in obstacles]
    if not valid_resources:
        return [0, 0]

    # Precompute opponent's nearest resource distance for tie-breaking
    def nearest_dist(x, y):
        best = None
        for rx, ry in valid_resources:
            d = cheb(x, y, rx, ry)
            if best is None or d < best:
                best = d
        return best if best is not None else 10**9

    opp_near_base = nearest_dist(ox, oy)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose nearest resource from the candidate (greedy but evaluated with opponent denial)
        self_near = None
        opp_near = None
        self_target = None
        for rx, ry in valid_resources:
            ds = cheb(nx, ny, rx, ry)
            if self_near is None or ds < self_near:
                self_near = ds
                self_target = (rx, ry)
        # Opponent distance to that same target (denial focus)
        rx, ry = self_target
        self_to_target = self_near
        opp_to_target = cheb(ox, oy, rx, ry)

        # Denial: want to keep opponent far from their nearest resource relative to us
        opp_near_after = nearest_dist(ox, oy)  # opponent doesn't move now; deterministic proxy

        # Safety: avoid moves that run adjacent to many obstacles (local trapping)
        adj_obs = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) in obstacles:
                adj_obs += 1

        # Value: prioritize reducing our distance; add denial by preferring targets that are relatively worse for opponent,
        # and favor moves that increase relative advantage over opponent's nearest pool distance.
        rel = opp_to_target - self_to_target
        val = (rel * 2000) - (self_to_target * 15) - (adj_obs * 3) - (opp_near_after * 0)

        # Small deterministic preference to not drift if equal: move toward increasing coordinate sum (stable)
        val += (nx + ny) * 1e-6

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]