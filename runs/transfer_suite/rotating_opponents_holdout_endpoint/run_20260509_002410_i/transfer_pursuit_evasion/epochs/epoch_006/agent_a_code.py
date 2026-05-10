def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    x, y, ex, ey = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursue" in role) or ("pursuit" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: abs(c[0] - ex) + abs(c[1] - ey))  # for evader: run to farthest corner

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        dist2 = d2(nx, ny, ex, ey)
        # Wall-run / boundary pressure
        boundary = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
        wall_score = (w - 1) - boundary  # larger means closer to boundary

        # Obstacle proximity penalty to avoid getting trapped
        near_obs = 0
        for ax, ay in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1), (nx + 1, ny + 1), (nx + 1, ny - 1), (nx - 1, ny + 1), (nx - 1, ny - 1)):
            if (ax, ay) in obs:
                near_obs += 1

        if pursuer:
            # Pursuer: minimize distance strongly; also prefer reducing both coordinate deltas (diagonal cutting).
            prev_dx, prev_dy = ex - x, ey - y
            new_dx, new_dy = ex - nx, ey - ny
            coord_gain = (abs(prev_dx) + abs(prev_dy)) - (abs(new_dx) + abs(new_dy))
            val = (-dist2 * 1000) + (coord_gain * 10) + (wall_score * 0.5) - (near_obs * 5)
        else:
            # Evader: maximize distance; run to corner opposite opponent and hug a wall deterministically.
            corner_dist = d2(nx, ny, target_corner[0], target_corner[1])
            corner_bias = (w * w + h * h) - corner_dist
            val = (dist2 * 1000) + (corner_bias * 5) + (wall_score * 20) - (near_obs * 5)

        if best_val is None or (val > best_val if not pursuer else val > best_val):
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # deterministic tie-break: lexicographic by deltas order
            if deltas.index((dx, dy)) < deltas.index(best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]