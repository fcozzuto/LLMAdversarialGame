def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_evader = any(k in role for k in ("evader", "evade", "escape", "runner"))
    opp_evader = any(k in opp_role for k in ("evader", "evade", "escape", "runner"))
    we_evader = self_evader and not opp_evader

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves = sorted(moves, key=lambda d: (d != (0, 0), abs(d[0]) + abs(d[1]) == 2, d[0], d[1]))

    def neigh_open(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if inb(nx, ny) and not blocked(nx, ny):
                    c += 1
        return c

    best_move = (0, 0)
    best_score = -10**18 if we_evader else 10**18

    # "Directly avoid" component: compute opponent direction and try to increase (or decrease) that separation.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy  # engine would keep us, but scoring should match resulting position
        d = dist2(nx, ny)
        open_n = neigh_open(nx, ny)
        # dead-end penalty for evader; corner preference for pursuer to speed capture attempts
        corner_bias = (nx in (0, w - 1) and ny in (0, h - 1))
        # also penalize moving closer in manhattan if evader wants to maximize separation
        man_sep = abs(nx - ox) + abs(ny - oy)
        man_cur = abs(sx - ox) + abs(sy - oy)
        if we_evader:
            dead_end_pen = -3 if open_n <= 2 else 0
            score = d + 0.8 * open_n + (2.5 if corner_bias else 0) + dead_end_pen + 0.6 * (man_sep - man_cur)
            if score > best_score:
                best_score, best_move = score, (dx, dy)
        else:
            # pursuer: minimize distance; prefer cells with more mobility to avoid getting stuck
            dead_end_pen = 3 if open_n <= 2 else 0
            score = -d + 0.2 * open_n - (2.0 if corner_bias else 0) - 0.3 * dead_end_pen + 0.1 * (man_sep - man_cur)
            if score < best_score:
                best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]