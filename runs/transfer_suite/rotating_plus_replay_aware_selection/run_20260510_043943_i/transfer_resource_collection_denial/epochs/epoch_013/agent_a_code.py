def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a resource where we are (deterministically) advantaged: maximize (opp_d - self_d).
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles or not inb(rx, ry):
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (od - sd, -sd, -od, rx, ry)  # prefer us being closer; then nearer overall
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    # If no reachable resources, drift away from opponent.
    if best is None:
        target_x, target_y = sx + (sx - ox), sy + (sy - oy)
    else:
        target_x, target_y = best

    # Choose a move that keeps us closest to the target while avoiding obstacles.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_target = dist(nx, ny, target_x, target_y)
        # Also discourage moves that give opponent immediate better access elsewhere.
        opp_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles or not inb(rx, ry):
                continue
            val = dist(ox, oy, rx, ry) - dist(nx, ny, rx, ry)
            if opp_best is None or val > opp_best:
                opp_best = val
        # Maximize our advantage margin against their likely nearest-resource behavior.
        adv = opp_best if opp_best is not None else 0
        cand = (adv, -d_to_target, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]