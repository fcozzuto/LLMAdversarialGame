def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if is_evader:
        far_corner = max([(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)],
                         key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        cx, cy = far_corner
    else:
        target_corner = max([(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)],
                             key=lambda c: - (abs(c[0] - sx) + abs(c[1] - sy)))
        cx, cy = target_corner

    def nearest_obs_dist(x, y):
        if not obs:
            return 10**9
        return min(abs(x - ax) + abs(y - ay) for ax, ay in obs)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        man = abs(nx - ox) + abs(ny - oy)
        eu2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        obs_d = nearest_obs_dist(nx, ny)

        if is_evader:
            # Maximize distance; also prefer staying away from obstacles; add slight bias to a far corner.
            val = (man, eu2, obs_d, abs(nx - cx) + abs(ny - cy))
            if best_val is None or val > best_val:
                best_val = val
                best = [dx, dy]
        else:
            # Minimize distance; also prefer increasing obstacle clearance; bias towards corner funnel.
            val = (-man, -eu2, obs_d, abs(nx - cx) + abs(ny - cy))
            if best_val is None or val > best_val:
                best_val = val
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]