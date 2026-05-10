def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role)
    opp_evader = ("evad" in opp_role) if opp_role else (not self_evader)

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),
             (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def neighbors(x, y):
        res = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                res.append((nx, ny))
        return res

    self_moves = neighbors(sx, sy)
    if not self_moves:
        return [0, 0]

    def opp_best_after(selfx, selfy):
        opp_opts = neighbors(ox, oy)
        if not opp_opts:
            return ox, oy
        best = None
        bestv = None
        for px, py in opp_opts:
            v = d2(selfx, selfy, px, py)
            if opp_evader:
                if best is None or v > bestv:
                    best, bestv = (px, py), v
            else:
                if best is None or v < bestv:
                    best, bestv = (px, py), v
        return best

    best_move = (sx, sy)
    if self_evader:
        bestv = None
        for nx, ny in self_moves:
            px, py = opp_best_after(nx, ny)
            v = d2(nx, ny, px, py)
            if bestv is None or v > bestv:
                bestv, best_move = v, (nx, ny)
        return [best_move[0] - sx, best_move[1] - sy]
    else:
        bestv = None
        for nx, ny in self_moves:
            px, py = opp_best_after(nx, ny)
            v = d2(nx, ny, px, py)
            if bestv is None or v < bestv:
                bestv, best_move = v, (nx, ny)
        return [best_move[0] - sx, best_move[1] - sy]