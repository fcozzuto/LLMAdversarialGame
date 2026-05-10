def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    obs_list = list(obs_set)

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_penalty(x, y):
        if not obs_list:
            return 0
        best = 10_000
        for ax, ay in obs_list:
            d2 = dist2(x, y, ax, ay)
            if d2 < best:
                best = d2
        # Strongly avoid stepping onto/adjacent obstacles; still deterministic.
        return 0 if best >= 4 else (40 if best == 0 else (12 if best == 1 else (6 if best == 2 else 2)))

    best = None
    best_move = [0, 0]
    # If pursuer, also lightly bias toward "cutting off" by moving toward the midpoint line.
    midx, midy = (sx + ox) / 2.0, (sy + oy) / 2.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_opp2 = dist2(nx, ny, ox, oy)
        obs_pen = obstacle_penalty(nx, ny)
        if is_evader:
            # Maximize distance; prefer positions that keep a bit away from obstacles.
            score = d_to_opp2 * 2.0 - obs_pen * 3.0 - 0.02 * dist2(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0)
        else:
            # Pursuer: minimize distance; avoid obstacles; add slight midline/axis bias to counter zigzag.
            score = -d_to_opp2 * 2.0 - obs_pen * 3.0 - 0.01 * dist2(nx, ny, midx, midy)

        # Deterministic tie-breaker: lexicographic by move order
        key = score
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return best_move