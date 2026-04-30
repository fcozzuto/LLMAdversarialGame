def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    xydirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx >= dy else dy

    # Pick a resource where we are relatively closer than the opponent
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Higher is better: we want ds small, and do large.
        desir = (do - ds)
        key = (desir, -do, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        # No resources: just drift to center to avoid getting stuck
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    # Choose move that reduces distance to target while avoiding obstacles
    candidates = []
    for dx, dy in xydirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dn = cheb(nx, ny, tx, ty)
        # Secondary tie-breaker: prefer moves that also keep distance advantage
        # relative to opponent.
        dno = cheb(ox, oy, tx, ty)
        candidates.append((( -dn, dno - dn, dx, dy ), (dx, dy)))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True, key=lambda x: x[0])
    return [candidates[0][1][0], candidates[0][1][1]]