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
    self_is_evader = ("evad" in sr)
    is_evader = self_is_evader  # if unknown, assume pursuer-like behavior for scoring is handled below

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    obs_list = list(obs)
    def min_obst_manh(x, y):
        best = 10**9
        for (bx, by) in obs_list:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
        return best if best != 10**9 else 99

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_val = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        d_to_opp = dist2(nx, ny, ox, oy)

        # Intercept-style bias: move slightly toward the opponent's direction.
        step_dx = 0 if ox == sx else (1 if ox > sx else -1)
        step_dy = 0 if oy == sy else (1 if oy > sy else -1)
        projected = (nx - (sx + step_dx), ny - (sy + step_dy))
        proj_pen = projected[0] * projected[0] + projected[1] * projected[1]

        # Stay away from obstacles; prefer remaining mobility near center.
        obst_bonus = min_obst_manh(nx, ny)
        center = dist2(nx, ny, cx, cy)
        mobility = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if safe(tx, ty):
                mobility += 1

        if is_evader:
            # Evader: maximize distance to pursuer, but don't crash into walls/obstacles.
            val = (d_to_opp * 1000) + (obst_bonus * 10) + (mobility * 3) - (center * 0.2) - (proj_pen * 0.05)
        else:
            # Pursuer: minimize distance to evader with intercept bias; avoid being cornered by obstacles.
            val = (-d_to_opp * 1000) + (obst_bonus * 10) + (mobility * 3) - (center * 0.2) - (proj_pen * 0.05)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move