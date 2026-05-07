def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose target: prioritize resources where we are closer than opponent.
    if resources:
        best = None
        for rx, ry in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            margin = od - sd  # bigger => we are closer
            key = (margin, -sd, -(rx + ry))  # deterministic tie-break
            if best is None or key > best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (None, -10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_to = dist(nx, ny, tx, ty)
        opp_to = dist(ox, oy, tx, ty)
        # Prefer moving toward target, and prefer increasing our advantage.
        # Also add slight penalty for stepping away from target.
        cur_self = dist(sx, sy, tx, ty)
        self_adv = opp_to - self_to
        key = (self_adv, -(self_to), (cur_self - self_to), -(nx + 31 * ny), 0)
        if best_move[0] is None or key > best_move[1]:
            best_move = (dx, key, (nx, ny))

    if best_move[0] is None:
        return [0, 0]
    return [best_move[0], 0] if best_move[2][0] == sx and best_move[2][1] != sy and best_move[0] == 0 else [best_move[0], best_move[2][1] - sy]