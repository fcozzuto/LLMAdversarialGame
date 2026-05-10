def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer claiming unclaimed cells while actively challenging opponent boundaries.
    base_dist_opp = abs(sx - ox) + abs(sy - oy)
    best_move = (0, 0)
    best = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0

        if (nx, ny) in opp_t:
            score += 100000  # direct flip
        if (nx, ny) in unclaimed:
            score += 8000
        if (nx, ny) in self_t:
            score -= 1200

        # If we step into a cell adjacent to opponent territory, it helps create a boundary contest.
        adj_opp = 0
        for adx, ady in neigh8:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in opp_t:
                adj_opp += 1
        score += adj_opp * 900

        # Move toward the opponent (but not by hugging our own territory).
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score += (base_dist_opp - dist_opp) * 45

        # Soft pull toward center to avoid getting boxed in.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += - (abs(nx - cx) + abs(ny - cy)) * 4

        # Discourage dead-ends near obstacles.
        obst_adj = 0
        for adx, ady in neigh8:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in obstacles:
                obst_adj += 1
        score -= obst_adj * 35

        if score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]