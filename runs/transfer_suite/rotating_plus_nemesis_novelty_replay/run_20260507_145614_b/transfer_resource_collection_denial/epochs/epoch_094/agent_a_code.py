def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        if sx + dx < 0 or sx + dx >= w or sy + dy < 0 or sy + dy >= h or (sx + dx, sy + dy) in obst:
            # fallback: axis
            if (sx + dx, sy) not in obst and 0 <= sx + dx < w:
                return [dx, 0]
            if (sx, sy + dy) not in obst and 0 <= sy + dy < h:
                return [0, dy]
            return [0, 0]
        return [dx, dy]

    # Pick the resource that we can reach sooner, breaking ties by reducing opponent reachability.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds, -do, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Greedy one-step: minimize our distance to target, and maximize opponent distance to target.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Also add a small term to prefer moves that increase our lead over time (relative distance).
        lead = (cheb(sx, sy, tx, ty) - ns) - (no - cheb(ox, oy, tx, ty))
        score = -ns + 0.3 * no + 0.1 * lead
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]