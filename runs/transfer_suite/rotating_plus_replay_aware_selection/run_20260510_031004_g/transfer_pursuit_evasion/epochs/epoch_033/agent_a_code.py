def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or (("pursuer" not in role) and ("chaser" not in role))

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Score: for evader maximize; for pursuer minimize. Deterministic tie-breakers included.
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy

        d = dist2(nx, ny, ox, oy)
        # Boundary-mobility bias (evader wants to avoid being squeezed; pursuer doesn't care much)
        wall_pen = (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))  # larger is better, away from walls
        # Directional bias: deterministic preference based on relative position
        dir_term = (nx - sx) * (nx - ox) + (ny - sy) * (ny - oy)

        if evader:
            val = d * 1000 + wall_pen * 3 + dir_term * 0.01
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < tuple(best_move))
        else:
            val = d * 1000 - wall_pen * 1 - dir_term * 0.01
            better = (best_val is None) or (val < best_val) or (val == best_val and (dx, dy) < tuple(best_move))
        if better:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]