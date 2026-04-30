def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    res_set = set(tuple(p) for p in resources)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return (dx * dx + dy * dy)

    best = None
    best_score = None
    # Deterministic tie-break order: moves list order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0.0

        if (nx, ny) in res_set:
            score += 10000.0

        if resources:
            d_res = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            score -= 3.0 * d_res
        else:
            score -= dist(nx, ny, w - 1, h - 1)

        d_opp = dist(nx, ny, ox, oy)
        score += 0.9 * d_opp  # discourage moving toward opponent

        # Mild preference to advance away from our corner toward center/top-left direction depending on start
        # (opponents start opposite; creates material change vs naive greedy).
        # Use a direction bias based on relative location.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= 0.02 * dist(nx, ny, cx, cy)

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best