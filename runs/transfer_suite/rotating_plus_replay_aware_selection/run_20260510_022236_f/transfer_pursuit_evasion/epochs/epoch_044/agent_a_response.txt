def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    # Small deterministic tie-break: prefer moves with larger dx, then dy.
    def tie_key(dx, dy):
        return (abs(dx) + abs(dy), dx, dy)

    best_val = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obs:
            val = -10**12 if not is_evader else -10**12
        else:
            dist = abs(nx - ox) + abs(ny - oy)
            # Wall proximity keeps moves from being "stuck" by boundary clamping.
            wall = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
            wall_pen = (0 if wall >= 2 else (4 - wall) * 2)

            # Obstacle avoidance: penalize being adjacent/near obstacles.
            obst_pen = 0
            if obs:
                for ex, ey in obs:
                    md = abs(nx - ex) + abs(ny - ey)
                    if md == 0:
                        obst_pen += 10**6
                    elif md == 1:
                        obst_pen += 25
                    elif md == 2:
                        obst_pen += 8

            if is_evader:
                # Maximize distance; also keep away from obstacles and corners.
                val = dist * 10 - wall_pen * 4 - obst_pen
            else:
                # Pursuer: minimize distance; also avoid corners/obstacles.
                val = -dist * 10 - wall_pen * 4 - obst_pen

        k = tie_key(dx, dy)
        if best_val is None or val > best_val or (val == best_val and k > tie_key(best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]