def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_resource_dist2(x, y):
        if not resources:
            cx = (w - 1) / 2.0
            cy = (h - 1) / 2.0
            dx = x - cx
            dy = y - cy
            return dx * dx + dy * dy
        best = None
        for rx, ry in resources:
            d = (x - rx) * (x - rx) + (y - ry) * (y - ry)
            if best is None or d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_res = nearest_resource_dist2(nx, ny)
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = (-d_res) + 0.15 * d_opp
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]