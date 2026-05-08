def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    # Precompute opponent distances
    best_res_score = {}
    for rx, ry in res:
        best_res_score[(rx, ry)] = md(ox, oy, rx, ry)

    # Evaluate immediate move by best net gain over all resources
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        val = 0
        for rx, ry in res:
            d_op = best_res_score[(rx, ry)]
            d_self = md(nx, ny, rx, ry)
            # Prefer being closer than opponent; also prefer taking nearby/soon wins
            net = (d_op - d_self)
            if (nx, ny) == (rx, ry):
                val += 1000000
            else:
                val += net * 5000 - d_self
        # Small tie-break: prefer moves that reduce distance to opponent nearest resource
        if resources:
            nr = min(res, key=lambda p: md(ox, oy, p[0], p[1]))
            val -= md(nx, ny, nr[0], nr[1]) * 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]