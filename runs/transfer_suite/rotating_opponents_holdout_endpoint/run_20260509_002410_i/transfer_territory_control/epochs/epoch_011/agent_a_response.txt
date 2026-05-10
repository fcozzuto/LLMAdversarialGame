def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def cell_gain(x, y):
        if (x, y) in obstacles:
            return -10**9
        base = 0
        if (x, y) in unclaimed:
            base += 100
        if (x, y) in self_t:
            base += 40
        if (x, y) in opp_t:
            base += 80  # flipping on entry enabled
        # Local expansion pressure: how many unclaimed adjacent cells
        adj_u = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in unclaimed:
                adj_u += 1
        base += 12 * adj_u
        # Prefer moving closer to opponent to enable counterclaims; also avoid getting stuck
        dist_self = abs(x - ox) + abs(y - oy)
        base += (18 if dist_self <= 3 else 0) - (dist_self // 2)
        # If staying, slight penalty to encourage progress unless already in good territory
        if x == sx and y == sy:
            base -= 6 if (sx, sy) not in self_t else 2
        return base

    best = [0, 0]
    best_score = cell_gain(sx, sy)
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        sc = cell_gain(nx, ny)
        if sc > best_score:
            best_score = sc
            best = [dx, dy]
        elif sc == best_score:
            # deterministic tie-break: prefer diagonal, then towards opponent, then towards increasing x, then y
            def pref(m):
                tx, ty = m
                diag = 1 if tx != 0 and ty != 0 else 0
                toward = - (abs((sx + tx) - ox) + abs((sy + ty) - oy))
                return (diag, toward, tx, ty)
            if pref([dx, dy]) > pref(best):
                best = [dx, dy]
    return best