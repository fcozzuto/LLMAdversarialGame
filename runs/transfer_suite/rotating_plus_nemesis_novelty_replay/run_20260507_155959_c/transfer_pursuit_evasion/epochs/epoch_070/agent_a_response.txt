def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.append((int(p[0]), int(p[1])))
        except Exception:
            pass
    obs_set = set(obstacles)

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or role == "evader"

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def mdist_to_obs(x, y):
        if not obstacles:
            return 99
        best = 99
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    best = None
    best_score = None

    if is_evader:
        # Prefer moving toward the farthest corner while maximizing distance from pursuer.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_from_p = man(nx, ny, ox, oy)
            d_to_t = man(nx, ny, target[0], target[1])
            # Make obstacles repulsive; slight bias to drift toward target.
            score = (d_from_p, d_to_t, mdist_to_obs(nx, ny))
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]
    else:
        # Pursuer: go for smallest distance; add "cutoff" bias toward maintaining approach alignment and obstacle safety.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_next = man(nx, ny, ox, oy)

            # Alignment cutoff: prefer moves that reduce max component separation (faster zigzag catch).
            sep_x = abs((ox - nx))
            sep_y = abs((oy - ny))
            cutoff = max(sep_x, sep_y)

            # Small bonus for moving toward opponent's general direction (not just Manhattan min).
            step_dir_x = 0 if ox == nx else (1 if ox > nx else -1)
            step_dir_y = 0 if oy == ny else (1 if oy > ny else -1)
            align = 1 if (dx == step_dir_x and dy == step_dir_y) else 0

            # Prefer not to get too close to obstacles (avoid getting stuck by zigzags).
            safe = mdist_to_obs(nx, ny)

            score = (-d_next, cutoff, -align, -safe)
            if best_score is None or score < best_score:
                best_score = score
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]