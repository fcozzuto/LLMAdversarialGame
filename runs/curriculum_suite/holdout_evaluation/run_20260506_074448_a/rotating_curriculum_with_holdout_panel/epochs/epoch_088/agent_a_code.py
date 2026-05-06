def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [(p[0], p[1]) for p in (observation.get("resources") or []) if 0 <= p[0] < w and 0 <= p[1] < h and (p[0], p[1]) not in obstacles]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    if not resources:
        best = (None, -10**18)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = -d2(nx, ny, cx, cy)
                if val > best[1]:
                    best = (dx, dy), val
        return list(best[0]) if best[0] is not None else [0, 0]

    opp_d_cur = min(d2(ox, oy, rx, ry) for rx, ry in resources)
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        self_best = 10**18
        opp_best_at = 10**18
        for rx, ry in resources:
            self_best = min(self_best, d2(nx, ny, rx, ry))
            opp_best_at = min(opp_best_at, d2(ox, oy, rx, ry))

        # Prefer moves that decrease our best distance more than they help the opponent.
        val = (opp_best_at - self_best)
        # Nudge toward center and away from current opponent "pressure"
        val += 0.01 * (d2(sx, sy, cx, cy) - d2(nx, ny, cx, cy))
        val += 0.001 * (opp_d_cur - opp_best_at)

        if val > best_val or (val == best_val and self_best < d2(sx, sy, resources[0][0], resources[0][1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]