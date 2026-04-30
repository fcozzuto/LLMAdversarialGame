def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((x, y) for x, y in obstacles)

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [[-1, -1], [0, -1], [1, -1], [-1, 0], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]

    if not resources:
        # Drift toward the map center deterministically
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9)
        res = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny, tx, ty)
            if (d, nx + ny) < best:
                best = (d, nx + ny)
                res = [dx, dy]
        return res

    # Target resource that we can reach sooner while keeping opponent farther (materially different from pure nearest)
    best_key = None
    best_t = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer: smallest ds; then largest do; then farthest from opponent to avoid contest
        key = (ds, -do, -(abs(rx - ox) + abs(ry - oy)))
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    # Greedy step towards target with obstacle avoidance
    cur_d = cheb(sx, sy, tx, ty)
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        d = cheb(nx, ny, tx, ty)
        # Slightly penalize moving closer to opponent (avoid getting blocked/contested)
        threat = cheb(nx, ny, ox, oy)
        candidates.append((d, -threat, dx, dy))
    if candidates:
        candidates.sort()
        # If tied, deterministic by dx,dy already in tuple ordering
        return [candidates[0][2], candidates[0][3]]

    return [0, 0]