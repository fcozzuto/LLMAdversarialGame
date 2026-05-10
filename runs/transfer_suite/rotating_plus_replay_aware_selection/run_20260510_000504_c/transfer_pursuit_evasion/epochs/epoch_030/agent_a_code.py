def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs)
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or not (("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role))
    resources = observation.get("resources", []) or []
    res = set(tuple(p) for p in resources)
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy
    def nearest_res_score(x, y):
        if not res:
            return 0
        best = 10**18
        for rx, ry in res:
            d = dist2(x, y, rx, ry)
            if d < best:
                best = d
        return -best
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        toward = -d if not i_am_evader else d
        res_bonus = nearest_res_score(nx, ny)
        trap_pen = -1 if (nx, ny) in res else 0
        val = toward + (3 * res_bonus) + trap_pen
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)
    if not ok(sx + best_move[0], sy + best_move[1]):
        for dx, dy in moves:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]