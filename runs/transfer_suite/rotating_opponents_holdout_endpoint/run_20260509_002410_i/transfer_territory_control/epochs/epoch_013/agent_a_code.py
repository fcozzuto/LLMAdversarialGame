def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = set(map(tuple, observation.get("resources") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dxdy = (0, 0)
    best_score = -10**18
    neigh_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in dirs:
        x, y = sx + dx, sy + dy
        if not inside(x, y) or (x, y) in obstacles:
            continue

        md = abs(x - ox) + abs(y - oy)
        s = -md

        in_opp = (x, y) in opp_t
        in_self = (x, y) in self_t
        in_unc = (x, y) in unclaimed
        in_res = (x, y) in resources

        if in_opp:
            s += 1200  # flipping target
        if in_unc:
            s += 420
        if in_res:
            s += 160
        if in_self:
            s += 40

        # Prefer capturing cells adjacent to opponent territory (frontier pressure).
        adj_opp = 0
        adj_unc = 0
        for nx, ny in neigh_dirs:
            ax, ay = x + nx, y + ny
            if inside(ax, ay):
                if (ax, ay) in opp_t:
                    adj_opp += 1
                if (ax, ay) in unclaimed:
                    adj_unc += 1
        s += 90 * adj_opp + 20 * adj_unc

        # Slightly avoid dead-ends near obstacles.
        wall = 0
        for nx, ny in neigh_dirs:
            ax, ay = x + nx, y + ny
            if not inside(ax, ay) or (ax, ay) in obstacles:
                wall += 1
        s -= 6 * wall

        if s > best_score:
            best_score = s
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]