def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_counts(nx, ny):
        adj_opp = 0
        adj_un = 0
        adj_self = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if not inb(ax, ay) or (ax, ay) in obs:
                    continue
                if (ax, ay) in opp:
                    adj_opp += 1
                if (ax, ay) in unclaimed:
                    adj_un += 1
                if (ax, ay) in selft:
                    adj_self += 1
        return adj_opp, adj_un, adj_self

    self_cnt = int(observation.get("self_territory_count", 0))
    opp_cnt = int(observation.get("opponent_territory_count", 0))
    trailing = 1 if self_cnt < opp_cnt else 0
    risk_bias = 1 if trailing else -1

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        adj_opp, adj_un, adj_self = adj_counts(nx, ny)

        if (nx, ny) in unclaimed:
            base = 6.0 if trailing else 4.0
            score = base + 2.0 * adj_opp + 1.5 * adj_un
            score -= 0.6 * (min(abs(nx - ox) + abs(ny - oy) for (ox, oy) in opp) if opp else 6)
        elif (nx, ny) in selft:
            score = 1.2 + 1.0 * adj_self + 1.3 * adj_un + 0.5 * adj_opp
            score -= 0.3 * (min(abs(nx - ox) + abs(ny - oy) for (ox, oy) in opp) if opp else 6)
        elif (nx, ny) in opp:
            score = 0.2 + 2.0 * adj_un + 0.5 * adj_opp + 0.3 * adj_self
            score += (1.2 * risk_bias) - 2.5 * (1 + max(0, adj_self))
            score -= 0.2 * (min(abs(nx - ox) + abs(ny - oy) for (ox, oy) in opp) if opp else 6)
        else:
            score = 0.3 + 1.0 * adj_un + 0.5 * adj_opp - 0.1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]