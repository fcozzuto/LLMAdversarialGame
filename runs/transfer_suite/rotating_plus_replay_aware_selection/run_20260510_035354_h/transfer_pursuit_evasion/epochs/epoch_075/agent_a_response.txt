def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in self_role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Evader aims for corner farthest from pursuer; pursuer aims for corner closest to evader.
    if is_evader:
        tx, ty = max(corners, key=lambda c: man(ox, oy, c[0], c[1]))
    else:
        tx, ty = min(corners, key=lambda c: man(ox, oy, c[0], c[1]))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_opp = man(nx, ny, ox, oy)
        d_corner = man(nx, ny, tx, ty)

        # Obstacle proximity penalty (deterministic, avoids aiming at tight obstacle-adjacent cells).
        obs_pen = 0
        for ox2, oy2 in obstacles:
            dd = abs(nx - ox2) + abs(ny - oy2)
            if dd == 0:
                obs_pen = 10
                break
            if dd <= 2:
                obs_pen += (3 - dd)

        # Small tie-breaker: prefer moves that continue moving away/toward consistently on evader/pursuer.
        axis_bias = 0
        if dx != 0:
            axis_bias = abs((nx - sx) - (ox - sx))
        else:
            axis_bias = abs((ny - sy) - (oy - sy))

        if is_evader:
            val = (10 * d_opp) + (-d_corner) - (2 * obs_pen) - axis_bias * 0.01
        else:
            val = (-10 * d_opp) + (-d_corner) - (2 * obs_pen) - axis_bias * 0.01

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]