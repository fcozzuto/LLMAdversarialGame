def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("hunter" in self_role)
    is_evader = ("evader" in self_role) or ("runner" in self_role)
    if not (is_pursuer or is_evader):
        is_pursuer = True

    obs = set()
    for b in (observation.get("obstacles") or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if is_pursuer:
        target_x, target_y = ox, oy
    else:
        tx, ty = None, None
        best_d = -1
        for cx, cy in corners:
            d = (cx - ox) * (cx - ox) + (cy - oy) * (cy - oy)
            if d > best_d:
                best_d = d
                tx, ty = cx, cy
        target_x, target_y = tx, ty

    def step_dir(a, b):
        if a == b:
            return 0
        return 1 if b > a else -1

    desired_dx = step_dir(sx, target_x)
    desired_dy = step_dir(sx, target_y)

    def score_move(nx, ny):
        dpo = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        dsd = abs(nx - sx - desired_dx) + abs(ny - sy - desired_dy)
        # Secondary: prefer keeping away from obstacles by maximizing local free space.
        free = 0
        for ddx, ddy in deltas[:8]:  # exclude (0,0) for neighborhood
            xx, yy = nx + ddx, ny + ddy
            if in_bounds(xx, yy):
                free += 1
        if is_pursuer:
            primary = -dpo
        else:
            primary = dpo
        return (primary, -dpo, -dsd, free)

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        val = score_move(nx, ny)
        if best is None or val > best:
            best = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]