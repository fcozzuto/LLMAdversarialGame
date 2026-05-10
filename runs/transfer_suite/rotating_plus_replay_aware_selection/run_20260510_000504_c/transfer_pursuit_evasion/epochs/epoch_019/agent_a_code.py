def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def xy(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        if isinstance(p, int):
            return int(p % w), int(p // w)
        return 0, 0

    sx, sy = xy(observation.get("self_position"))
    ox, oy = xy(observation.get("opponent_position"))

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        x, y = xy(p)
        obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    i_am_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    opp_is_evader = ("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role)
    if "evader" in self_role: i_am_evader = True
    if "evader" in opp_role: opp_is_evader = True
    evader_mode = i_am_evader or (not opp_is_evader)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def wall_dist(x, y):
        dx = x if x < (w - 1 - x) else (w - 1 - x)
        dy = y if y < (h - 1 - y) else (h - 1 - y)
        return dx if dx < dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy
        e = wall_dist(nx, ny)
        if evader_mode:
            score = d2 * 10 + e * 1.5
        else:
            score = -d2 * 10 + e * 0.3
        if best is None or (score > best_score):
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best