def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.append((int(p[0]), int(p[1])))
    obs_set = set(obstacles)

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or role == "evader"

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs_set

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def nearest_obs_dist(x, y):
        if not obstacles:
            return 10**9
        best = 10**9
        for ax, ay in obstacles:
            d = manhattan(x, y, ax, ay)
            if d < best:
                best = d
        return best

    best_score = None
    best_move = [0, 0]
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = manhattan(nx, ny, ox, oy)
        d_obs = nearest_obs_dist(nx, ny)
        # Evader: maximize distance from pursuer, avoid stepping near obstacles (may trap).
        # Pursuer: minimize distance to pursuer, avoid obstacles.
        if is_evader:
            score = (d_opp * 1000) + (d_obs) - (0 if (dx == 0 and dy == 0) else 0)
            key = (score, -i)
        else:
            score = (-d_opp * 1000) + (d_obs)
            key = (score, -i)
        if best_score is None or key > best_score:
            best_score = key
            best_move = [dx, dy]

    if best_score is None:
        return [0, 0]
    return best_move