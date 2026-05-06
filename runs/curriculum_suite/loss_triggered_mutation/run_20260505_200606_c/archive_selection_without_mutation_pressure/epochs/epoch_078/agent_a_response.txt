def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = p[0], p[1]
            if (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        if (nx, ny) in obstacles:
            return None
        return nx, ny

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        ns = legal(sx, sy, dx, dy)
        if ns is None:
            continue
        nx, ny = ns

        # Choose the most favorable resource: self closer than opponent (large d_opp - d_self),
        # then prefer smaller self distance for that same resource.
        best_gap = -10**18
        best_sd = 10**18
        for rx, ry in res:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            gap = d_opp - d_self
            if gap > best_gap or (gap == best_gap and d_self < best_sd):
                best_gap, best_sd = gap, d_self

        # Also keep some separation from opponent to reduce interference in sweep-like play.
        score = best_gap * 1000 - best_sd + 0.5 * abs(ny - oy) - 0.1 * abs(nx - ox)

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]