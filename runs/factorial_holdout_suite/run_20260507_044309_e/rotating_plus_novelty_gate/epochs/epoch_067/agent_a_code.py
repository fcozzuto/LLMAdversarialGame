def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if resources:
        for dx, dy, nx, ny in valid:
            if (nx, ny) in set(tuple(r) for r in resources):
                return [dx, dy]

    # Choose a target resource that I can reach before the opponent; add a bonus for opponent-row "sweep" interception.
    opp_target = None
    best_val = None
    opp_row = oy
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gain = do - dme  # positive means I reach sooner
        row_bonus = 2 if ry == opp_row else 0
        val = gain * 5 - dme + row_bonus
        if best_val is None or val > best_val or (val == best_val and (rx, ry) < opp_target):
            opp_target = (rx, ry)
            best_val = val
    if opp_target is None:
        return [0, 0]
    tx, ty = opp_target

    # Move greedily toward the chosen target, with slight tie-break for reducing opponent distance too.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in valid:
        me_dist = cheb(nx, ny, tx, ty)
        opp_dist = cheb(ox, oy, tx, ty)
        # Opponent distance doesn't change, but we tie-break to prefer moves that keep closer to the same target row.
        score = -me_dist + (1 if ny == opp_row else 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move if best_move is not None else [0, 0]