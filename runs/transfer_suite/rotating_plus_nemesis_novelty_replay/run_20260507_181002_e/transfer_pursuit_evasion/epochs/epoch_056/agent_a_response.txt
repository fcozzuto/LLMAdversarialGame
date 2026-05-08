def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    moves = [(0, 0), (1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    obs_list = list(obstacles)
    def obstacle_penalty(x, y):
        if not obs_list:
            return 0.0
        md = 10**9
        for px, py in obs_list:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        if md <= 0:
            return -1000.0
        if md == 1:
            return -3.0
        if md == 2:
            return -1.5
        return -0.1 * md

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        # Center a bit to avoid corner trapping when evading; harmless otherwise
        center_boost = -0.02 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        if self_is_evader:
            score = d + center_boost + obstacle_penalty(nx, ny)  # maximize escape distance
        else:
            score = -d + center_boost + obstacle_penalty(nx, ny)  # minimize distance
        if best is None or score > best_score + 1e-12:
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return best