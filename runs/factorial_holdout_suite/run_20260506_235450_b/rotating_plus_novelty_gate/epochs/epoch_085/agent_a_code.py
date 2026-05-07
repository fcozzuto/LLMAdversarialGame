def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                rs.append((x, y))
    if not rs:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        # Choose the resource where we have maximum distance advantage over opponent.
        local_best = (-10**18, 10**9, 10**9)
        for rx, ry in rs:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            advantage = do - ds
            # Prefer larger advantage, then closer, then deterministic coordinate tie-break.
            cand = (advantage, -ds, -(rx + ry))
            if cand > local_best:
                local_best = cand
        score = local_best[0] * 1000000 + local_best[1]
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]