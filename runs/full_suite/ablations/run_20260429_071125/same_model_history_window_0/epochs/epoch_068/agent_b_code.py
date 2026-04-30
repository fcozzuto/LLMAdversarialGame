def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    if (x, y) in set((p[0], p[1]) for p in resources):
        return [0, 0]

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    deltas = [(dx, dy) for dx in dxs for dy in dys]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a target resource: prefer ones we can reach first, else closest/most valuable by bias.
    best = None
    best_key = None
    rx = ry = None
    for r in resources:
        tx, ty = r
        sd = dist(x, y, tx, ty)
        od = dist(ox, oy, tx, ty)
        # Lower is better: prioritize un-contested or faster-to-reach.
        key = (0 if sd <= od else 1, sd + 0.2 * (sd - od))
        if best_key is None or key < best_key:
            best_key = key
            best = r
            rx, ry = tx, ty

    if best is None:
        # No resources visible: drift toward center.
        rx, ry = (w - 1) / 2.0, (h - 1) / 2.0

    # Evaluate moves: avoid obstacles, minimize distance to target; slightly maximize distance from opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        # Prefer moves that reduce our distance to target.
        if isinstance(rx, float):
            d_t = abs(nx - rx) + abs(ny - ry)
        else:
            d_t = dist(nx, ny, rx, ry)
        d_o = dist(nx, ny, ox, oy)

        # If target is likely contested (opponent closer), add stronger anti-approach.
        contested = 0
        if best is not None and (dist(ox, oy, rx, ry) < dist(x, y, rx, ry)):
            contested = 1
        score = d_t - (0.08 + 0.12 * contested) * d_o

        if best_score is None or score < best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]