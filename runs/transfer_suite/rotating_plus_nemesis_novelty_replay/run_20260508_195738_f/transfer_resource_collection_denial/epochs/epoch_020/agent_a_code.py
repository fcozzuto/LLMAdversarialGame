def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx = 0 if ox > sx else (w - 1 if ox < sx else sx)
        ty = 0 if oy > sy else (h - 1 if oy < sy else sy)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [int(dx), int(dy)]

    # Choose targets that we can reach earlier than the opponent.
    best_target = None
    best_margin = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = manhattan(sx, sy, rx, ry)
        od = manhattan(ox, oy, rx, ry)
        margin = sd - od  # want smaller (more negative)
        # tie-break toward closer resources
        if best_margin is None or margin < best_margin or (margin == best_margin and sd < best_target[2]):
            best_margin = margin
            best_target = (rx, ry, sd)

    tx, ty, _ = best_target

    # Evaluate each move by improving margin vs the best contested target.
    best_move = (0, 0)
    best_score = -10**18
    best_dist = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Margin over all resources (helps switch if another becomes better immediately).
        local_best = None
        local_sd_best = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            sd = manhattan(nx, ny, rx, ry)
            od = manhattan(ox, oy, rx, ry)
            margin = od - sd  # want larger (opponent farther / we closer)
            if local_best is None or margin > local_best or (margin == local_best and sd < local_sd_best):
                local_best = margin
                local_sd_best = sd

        # Also strongly prefer getting closer to the chosen primary target.
        d_primary = manhattan(nx, ny, tx, ty)

        # If stepping onto a resource, this should dominate.
        on_resource = 1 if (nx, ny) == (tx, ty) else 0
        score = (local_best * 1000) + (on_resource * 10**8) - d_primary

        if score > best_score or (score == best_score and d_primary < best_dist):
            best_score = score
            best_dist = d_primary
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]