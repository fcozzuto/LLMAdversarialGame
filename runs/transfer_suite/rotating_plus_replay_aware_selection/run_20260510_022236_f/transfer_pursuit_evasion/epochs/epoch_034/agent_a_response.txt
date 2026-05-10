def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "")
    is_evader = "evader" in role.lower()

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    # For evader, also bias toward the farthest corner from the pursuer while avoiding obstacles.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy
        wd = wall_dist(nx, ny)

        if is_evader:
            # Primary: maximize distance; Secondary: stay away from walls; Tertiary: drift toward far corner.
            cc = abs(far_corner[0] - nx) + abs(far_corner[1] - ny)
            score = (d2, wd, -cc)
        else:
            # Primary: minimize distance; Secondary: stay away from walls; Tertiary: move with axis alignment toward opponent.
            axis = -(abs(nx - ox) + abs(ny - oy))
            score = (-d2, wd, axis)

        # Deterministic tie-break: prefer smaller dx, then smaller dy.
        tb = (score, abs(dx), abs(dy), dx, dy)
        if best is None or tb > best:
            best = tb
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]