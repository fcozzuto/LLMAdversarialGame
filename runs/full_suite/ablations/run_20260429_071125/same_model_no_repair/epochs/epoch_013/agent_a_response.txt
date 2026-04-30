def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    adj4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    adj8 = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    resset = {(r[0], r[1]) for r in resources}
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def obstacle_pen(x, y):
        if (x, y) in occ:
            return 10**6
        p = 0
        for dx, dy in adj4:
            if (x + dx, y + dy) in occ:
                p += 6
        # light penalty for being near blocked corners/diagonals
        for dx, dy in adj8:
            if (x + dx, y + dy) in occ:
                p += 1
        return p

    # Choose best move deterministically by score, tie-break by move order
    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pen = obstacle_pen(nx, ny)
        if pen >= 10**5:
            continue

        # Resource objective: nearest resource (prefer staying if already on it)
        if resources:
            if (nx, ny) in resset:
                res_d = 0
            else:
                # nearest by manhattan
                res_d = min(dist(nx, ny, rx, ry) for (rx, ry) in resset) if resset else 10**9
        else:
            res_d = 0

        # Prefer increasing distance from opponent slightly (reduce interference)
        opp_d = dist(nx, ny, ox, oy)

        # Center bias to spread and avoid getting stuck
        center_b = -0.03 * (((nx - cx) ** 2 + (ny - cy) ** 2) ** 0.5)

        # If opponent is adjacent, prioritize stepping away unless it blocks resource capture
        adj_opp = 1 if opp_d <= 1 else 0

        val = 0
        if resources:
            val += -2.2 * res_d
            val += (5.0 if (nx, ny) in resset else 0.0)
        val += 0.12 * opp_d
        val += center_b
        val -= pen
        val -= 2.0 * adj_opp * (1 if opp_d == 0 else 0)

        # Deterministic tie-break via move order (implicit by first max)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]