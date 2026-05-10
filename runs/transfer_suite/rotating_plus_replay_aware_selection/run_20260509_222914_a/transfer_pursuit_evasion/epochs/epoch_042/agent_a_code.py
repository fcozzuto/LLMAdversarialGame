def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = []
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.append((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("evasion" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_min_dist(x, y):
        if not obstacles:
            return 10**6
        dmin = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < dmin:
                dmin = d
        return dmin

    def score(x, y):
        d = abs(x - ox) + abs(y - oy)
        od = obs_min_dist(x, y)
        # Discourage stepping adjacent to obstacles; avoid being trapped
        obs_pen = 0.0
        if od <= 0:
            obs_pen = 1e6
        elif od == 1:
            obs_pen = 120.0
        elif od == 2:
            obs_pen = 50.0
        else:
            obs_pen = 1.0 / (od + 1)

        # If we're pursuer: minimize distance. If evader: maximize distance.
        if is_evader:
            # Prefer moving away; add slight preference for farther-from-obstacles.
            return (d * 1000.0) + (od * 3.0) - obs_pen
        else:
            # Prefer moving closer; add slight preference for farther-from-obstacles (more space).
            return (-d * 1000.0) + (od * 2.0) - obs_pen

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score(nx, ny)
        if best_val is None:
            best_val = v
            best_move = [dx, dy]
        else:
            if is_evader:
                if v > best_val:
                    best_val = v
                    best_move = [dx, dy]
            else:
                if v > best_val:
                    best_val = v
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]