def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        # Chebyshev distance for king moves
        return dx if dx > dy else dy

    # Choose a target resource that is both reachable and relatively unsafe for the opponent
    if resources:
        best = None
        best_val = None
        for rx, ry in resources:
            dS = dist((sx, sy), (rx, ry))
            dO = dist((ox, oy), (rx, ry))
            # Prefer closer to self, farther from opponent
            val = dS - 0.8 * dO
            if best_val is None or val < best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w // 2, h // 2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            moves.append((dx, dy, nx, ny))

    # If current location is blocked (unlikely), allow staying
    if not moves:
        return [0, 0]

    def obstacle_penalty(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = x + ax, y + ay
                if (xx, yy) in obstacles:
                    p += 1
        return p

    # Evaluate each move deterministically
    best_move = None
    best_score = None
    for dx, dy, nx, ny in moves:
        if (nx, ny) in obstacles:
            continue  # avoid obstacles when possible
        d_to_t = dist((nx, ny), (tx, ty))
        d_to_o = dist((nx, ny), (ox, oy))
        # Encourage approaching target, discourage letting opponent get close, avoid obstacle clutter
        score = -d_to_t + 0.35 * d_to_o - 0.15 * obstacle_penalty(nx, ny)
        # Deterministic tie-break: fixed order by dx,dy preference toward movement
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]