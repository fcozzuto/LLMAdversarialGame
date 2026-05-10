def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        for ax, ay in obstacles:
            if ax == x and ay == y:
                return True
        return False

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If no visible resources, drift to center-ish while denying opponent by moving toward its nearest resource.
    target = None
    if resources:
        # Choose closest resource with deterministic tie-break: (distance, x, y)
        best = None
        for rx, ry in resources:
            d = dist(rx, ry, sx, sy)
            cand = (d, rx, ry)
            if best is None or cand < best:
                best = cand
        target = (best[1], best[2])
    else:
        # Predict: head to opponent's side a bit
        target = (w - 1 - ox if ox < w / 2 else 0, h - 1 - oy if oy < h / 2 else 0)

    # Optional defense: if very close to opponent, bias to reduce their distance to nearest resource by blocking directionally.
    close_to_op = dist(sx, sy, ox, oy) <= 2

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if blocked(nx, ny):
                continue
            deltas.append((dx, dy))

    # Deterministic move ordering for tie-break
    deltas.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))

    best_move = (0, 0)
    best_score = None
    tx, ty = target

    # Estimate how much we would interfere with opponent
    # (lower score is better)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        my_d = dist(nx, ny, tx, ty)

        if close_to_op:
            # Move to keep opponent from reaching our target quickly.
            opp_d = dist(ox, oy, tx, ty)
            new_opp_d = dist(ox, oy, tx, ty)  # opponent position unchanged now; we still use direction bias
            # Directional denial: prefer steps that move toward line between opponent and target
            line_bias = abs((tx - ox) - (nx - ox)) + abs((ty - oy) - (ny - oy))
        else:
            line_bias = 0

        score = (my_d, line_bias, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]