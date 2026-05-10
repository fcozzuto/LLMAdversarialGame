def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    is_evader = ("evad" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_list = list(obs)

    def min_obst_manh(x, y):
        if not obs_list:
            return 99
        best = 99
        for bx, by in obs_list:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
        return best

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_score = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        d2 = dist2(nx, ny, ox, oy)
        mob = min_obst_manh(nx, ny)

        if not is_evader and d2 == 0:
            return [dx, dy]
        if is_evader and d2 == 0:
            continue

        center_dx = nx - (w - 1) / 2.0
        center_dy = ny - (h - 1) / 2.0
        center_pen = (center_dx * center_dx + center_dy * center_dy) / 1000.0

        if is_evader:
            score = d2 + 0.2 * mob - 0.3 * center_pen
        else:
            score = -d2 + 0.2 * mob - 0.15 * center_pen

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_score is not None else [0, 0]