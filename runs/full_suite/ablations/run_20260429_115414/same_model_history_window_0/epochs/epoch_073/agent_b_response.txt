def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(x, y):
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y

    def d(a, b, c, d2):  # chebyshev
        dx = a - c; dy = b - d2
        return dx if dx >= 0 else -dx if dx < 0 else None

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Precompute resource list for speed and determinism
    res = [tuple(r) for r in resources]

    def nearest_dist(px, py):
        best = 10**9
        for rx, ry in res:
            t = cheb(px, py, rx, ry)
            if t < best: best = t
        return best if best != 10**9 else 0

    # If no resources, just move away from opponent deterministically
    if not res:
        best = None; bestv = -10**18
        for dx, dy in moves:
            nx, ny = clamp(sx + dx, sy + dy)
            if (nx, ny) in obstacles: continue
            v = cheb(nx, ny, ox, oy)
            if best is None or v > bestv:
                bestv = v; best = [dx, dy]
        return best if best is not None else [0, 0]

    my_near_before = nearest_dist(sx, sy)
    # Targeting + disruption heuristic
    best = [0, 0]; bestv = -10**18
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles: continue

        my_near = nearest_dist(nx, ny)
        # slight preference for moves that reduce distance more
        delta_my = my_near_before - my_near

        # Encourage positions that keep opponent farther from resources (indirect)
        opp_near = nearest_dist(ox, oy)
        # also add small term to increase distance to opponent (avoid immediate contests)
        sep = cheb(nx, ny, ox, oy)

        # Deterministic tie-breakers: prefer diagonal/forward toward target-ish
        signx = 1 if nx > sx else (-1 if nx < sx else 0)
        signy = 1 if ny > sy else (-1 if ny < sy else 0)
        diag_bonus = 0.1 if dx != 0 and dy != 0 else 0.0

        v = (delta_my * 10.0) + (sep * 0.05) + (opp_near * 0.0) + diag_bonus \
            - (0.001 * (abs(dx) + abs(dy)))  # keep deterministic
        if v > bestv:
            bestv = v; best = [dx, dy]

    return best