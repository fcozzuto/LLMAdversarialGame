def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = w // 2, h // 2

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0

        if (nx, ny) in opp_t:
            score += 2500
        elif (nx, ny) in unclaimed:
            score += 180
        elif (nx, ny) in self_t:
            score += 30

        # Prefer progressing toward the center (opponent tends to claim it)
        d_center = abs(nx - cx) + abs(ny - cy)
        score += -2 * d_center

        # Prefer to be closer than the opponent to the chosen cell
        d_opp = abs(nx - ox) + abs(ny - oy)
        score += -1 * d_opp

        # Blocking/contesting: if close to opponent, favor moves that take/claim nearby cells
        d_self_opp = abs(sx - ox) + abs(sy - oy)
        if d_self_opp <= 6:
            if (nx, ny) in unclaimed:
                score += 80
            if d_opp <= 2 and (nx, ny) in unclaimed:
                score += 120

        # Slight preference to reduce our distance to the center compared to current
        score += (abs(sx - cx) + abs(sy - cy) - d_center)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]