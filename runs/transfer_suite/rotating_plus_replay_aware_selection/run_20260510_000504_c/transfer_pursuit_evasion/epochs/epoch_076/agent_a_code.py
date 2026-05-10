def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("evader" in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def closest_obstacle_dist(x, y):
        if not obstacles:
            return 999999
        dmin = 999999
        for a, b in obstacles:
            d = abs(x - a) + abs(y - b)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    break
        return dmin

    target_corner = (0, h - 1) if (ox >= w // 2) else (w - 1, 0) if (oy < h // 2) else (w - 1, h - 1) if (ox < w // 2) else (0, 0)

    best_move = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        d_ob = closest_obstacle_dist(nx, ny)

        if is_evader:
            corner_bias = abs(nx - target_corner[0]) + abs(ny - target_corner[1])
            # Maximize distance from pursuer, prefer keeping away from obstacles, and drift to a safe corner.
            val = (dist_to_opp * 1000 + corner_bias) + d_ob
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < best_move)
        else:
            # Minimize distance to pursuer, prefer more obstacle clearance, deterministic tie-break by smaller (dx,dy).
            val = dist_to_opp * 1000 - d_ob
            better = (best_val is None) or (val < best_val) or (val == best_val and (dx, dy) < best_move)

        if better:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]