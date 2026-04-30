def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        if not resources:
            dist_center = abs(nx - center_x) + abs(ny - center_y)
            val = -dist_center
        else:
            # Evaluate best resource we could "claim" relative to opponent
            best_gain = None
            best_self_d = None
            best_opp_d = None
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                gain = od - sd  # larger is better (we closer than opponent)
                if best_gain is None or gain > best_gain or (gain == best_gain and (sd < best_self_d or (sd == best_self_d and od > best_opp_d))):
                    best_gain = gain
                    best_self_d = sd
                    best_opp_d = od
            # Small preference for shorter self distance to avoid stalling
            val = (best_gain * 100) - best_self_d

        # Tie-break deterministically by move ordering and then by resulting position
        if best is None or val > best[0] or (val == best[0] and (dx, dy) < best[1]):
            best = (val, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [dx, dy]