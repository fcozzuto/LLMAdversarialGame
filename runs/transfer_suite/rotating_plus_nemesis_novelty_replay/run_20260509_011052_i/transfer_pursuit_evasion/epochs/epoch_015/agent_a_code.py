def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y):
        dx = x - ox
        dy = y - oy
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(x, y):
        dx = x - ox
        dy = y - oy
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    best = (10**9, 10**9, 10**9, 10**9)
    best_move = (0, 0)
    # Prefer moves that step onto/closest to opponent, with mild obstacle/edge caution.
    # Deterministic tie-break favors dx,dy that reduce relative vector.
    relx = ox - sx
    rely = oy - sy
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        c = cheb(nx, ny)
        m = man(nx, ny)
        edge_caution = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_caution = 1
        toward = 0
        if relx == 0:
            toward += 0
        else:
            toward += 0 if (dx == 0) else (1 if (dx > 0) == (relx > 0) else 0)
        if rely == 0:
            toward += 0
        else:
            toward += 0 if (dy == 0) else (1 if (dy > 0) == (rely > 0) else 0)
        # Primary: smallest Chebyshev to opponent (fastest exact-step convergence for dx/dy in {-1,0,1})
        # Secondary: smallest Manhattan
        # Tertiary: avoid edges slightly
        # Quaternary: deterministic "toward" preference
        val = (c, m, edge_caution, -toward)
        if val < best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]