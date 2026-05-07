def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    def clamp_move(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return sx, sy
        if (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = clamp_move(sx + dx, sy + dy)
        if (nx, ny) == (sx, sy) and (dx, dy) != (0, 0):
            continue

        # Evaluate by best target we could secure next; also bias toward resource-denial.
        local_best = -10**18
        for (rx, ry) in res:
            self_d = md((nx, ny), (rx, ry))
            opp_d = md((ox, oy), (rx, ry))
            # Prefer where we are closer than opponent; tie-break by absolute distance.
            val = (opp_d - self_d) * 100 - self_d
            # Small bias to avoid walking into dead-ends near the opponent line by discouraging
            # moving closer to opponent relative to resources.
            local_best = max(local_best, val)
        # If we can get an immediate move onto a resource, prioritize heavily.
        if (nx, ny) in res:
            local_best += 10**6

        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]