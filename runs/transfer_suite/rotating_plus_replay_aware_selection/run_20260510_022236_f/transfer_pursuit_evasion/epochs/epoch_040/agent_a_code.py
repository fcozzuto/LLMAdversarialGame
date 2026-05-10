def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.append((x, y))
    obs_set = set(obs)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    def obstacle_penalty(x, y):
        pen = 0
        for ox2, oy2 in obs:
            md = abs(x - ox2) + abs(y - oy2)
            if md == 0:
                return 10**9
            if md == 1:
                pen += 8
            elif md == 2:
                pen += 3
        return pen

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue

        if nx == ox and ny == oy:
            if not is_evader:
                return [dx, dy]

        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        wd = wall_dist(nx, ny)
        op = obstacle_penalty(nx, ny)

        # Deterministic scoring
        if is_evader:
            dist_term = d2
            corner_term = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
            center_term = wd * 2
            score = dist_term * 5 + corner_term + center_term - op
        else:
            dist_term = -d2
            corner_term = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
            center_term = -abs(wd - (min(w, h) // 2)) * 0.5
            score = dist_term * 5 + corner_term + center_term - op

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]