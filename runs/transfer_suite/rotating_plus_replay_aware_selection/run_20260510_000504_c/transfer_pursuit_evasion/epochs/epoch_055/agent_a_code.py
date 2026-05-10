def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.append((int(x), int(y)))
        except:
            pass

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("evad" in opponent_role) or ("hunter" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_obs_d(x, y):
        if not obstacles:
            return 99
        dmin = 99
        for bx, by in obstacles:
            d = abs(x - bx) + abs(y - by)
            if d < dmin:
                dmin = d
        return dmin

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist_after = max(abs(nx - ox), abs(ny - oy))  # zigzag-resistant (chebyshev)
        obs_d = nearest_obs_d(nx, ny)

        # obstacle penalty increases when close; deterministic
        obs_pen = 0
        if obs_d < 3:
            obs_pen = (3 - obs_d) * 5
        obs_pen += (2 if (nx, ny) == (ox, oy) else 0)  # tiny tie-break

        # pursuer: minimize distance; evader: maximize distance
        val = dist_after * (1 if is_pursuer else -1) + obs_pen * (1 if is_pursuer else 0.7)
        if best is None:
            best, best_move = val, [dx, dy]
        else:
            better = val < best if is_pursuer else val > best
            if better or (val == best and (dx, dy) < (best_move[0], best_move[1])):
                best, best_move = val, [dx, dy]

    return [int(best_move[0]), int(best_move[1])]