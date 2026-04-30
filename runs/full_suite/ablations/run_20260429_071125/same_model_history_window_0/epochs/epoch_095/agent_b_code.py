def choose_move(observation):
    x0, y0 = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        dx = 0
        dy = 0
        return [dx, dy]

    # Deterministic evaluation: choose move that maximizes our "resource advantage"
    for dx, dy in moves:
        x1, y1 = x0 + dx, y0 + dy
        if not inb(x1, y1):
            continue
        # Prefer getting to resources where we are (and will be) closer than opponent
        my_best = None
        for rx, ry in resources:
            myd = max(abs(rx - x1), abs(ry - y1))
            opd = max(abs(rx - ox), abs(ry - oy))
            # Higher is better: we want opd - myd
            val = (opd - myd) - 0.05 * myd + 0.01 * opd
            if my_best is None or val > my_best:
                my_best = val
        # Small bias to keep some distance from opponent (discourage stepping into tight races)
        my_opp_dist = max(abs(ox - x1), abs(oy - y1))
        cur_opp_dist = max(abs(ox - x0), abs(oy - y0))
        opp_bias = 0.02 * (my_opp_dist - cur_opp_dist)
        score = my_best + opp_bias
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score and best is not None:
            # Deterministic tie-break: prefer smaller |dx|+|dy| then lexicographic
            if (abs(dx) + abs(dy), dx, dy) < (abs(best[0]) + abs(best[1]), best[0], best[1]):
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]