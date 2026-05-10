def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Pick target: maximize how much sooner we can reach than opponent; if unclear, prefer nearest for us.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (do - ds, -ds, rx, ry)  # prioritize positive advantage, then closer, then deterministic coords
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # If opponent is already much closer, act more like a denier: get between us and them by moving to cell
    # that increases their distance while still trending toward the same best target.
    opp_closer = man(ox, oy, tx, ty) <= man(sx, sy, tx, ty)

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(nx, ny, ox, oy)
        opp_target_dist = man(ox, oy, tx, ty)

        # Encourage reducing our distance; if opp_closer, also discourage opponent by increasing their reach-to-us.
        # Secondary: avoid being in/near opponent by considering direct distance.
        score = (0,)
        if opp_closer:
            score = (-ds2, do2, -(opp_target_dist), nx, ny)
        else:
            score = (-ds2, -(do2), nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]