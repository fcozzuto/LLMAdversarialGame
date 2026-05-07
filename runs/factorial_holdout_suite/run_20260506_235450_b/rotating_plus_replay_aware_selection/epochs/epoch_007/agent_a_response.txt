def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1 if sx < w // 2 else 0), (h - 1 if sy < h // 2 else 0)
        best = None
        for dx, dy, nx, ny in legal:
            d = abs(nx - tx) + abs(ny - ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    def opp_speed_bias(px, py):
        # If opponent is likely sweeping, prefer resources away from their current row/col line
        # to prevent being out-raced.
        return abs(px - ox) + abs(py - oy)

    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        # Evaluate this immediate move by the best resource we can contest now.
        local_best = None
        local_best2 = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            self_t = abs(nx - rx) + abs(ny - ry)
            opp_t = abs(ox - rx) + abs(oy - ry)
            # Primary: how much sooner we arrive than opponent (lower is better overall).
            # Secondary: minimize our time; tertiary: bias away from opponent to avoid sweep trapping.
            comp = self_t - opp_t
            t2 = self_t
            t3 = opp_speed_bias(rx, ry)
            key = (comp, t2, t3)
            if local_best is None or key < local_best:
                local_best = key
                local_best2 = (rx, ry)
        score = local_best
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]