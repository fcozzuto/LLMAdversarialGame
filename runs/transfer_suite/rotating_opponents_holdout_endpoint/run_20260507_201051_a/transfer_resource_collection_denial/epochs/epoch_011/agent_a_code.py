def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            score = (ds, -do, rx, ry)
            if best is None or score < best[0]:
                best = (score, rx, ry)
        if best is not None:
            _, tx, ty = best
        else:
            tx, ty = w // 2, h // 2
    else:
        tx, ty = w // 2, h // 2

    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        cur = man(nx, ny, tx, ty)
        # Prefer moves that also deny opponent by increasing their distance to target
        deny = -man(nx, ny, ox, oy)
        key = (cur, deny, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    if best_move is None:
        # Try to stay if possible, else any valid move
        if in_bounds(sx, sy):
            return [0, 0]
        for dx, dy in dirs:
            if in_bounds(sx + dx, sy + dy):
                return [dx, dy]
    return best_move[1] if best_move else [0, 0]