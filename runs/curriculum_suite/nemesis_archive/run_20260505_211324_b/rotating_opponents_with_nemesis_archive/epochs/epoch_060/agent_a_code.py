def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not res:
        # drift toward center while avoiding immediate opponent proximity
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy, nx, ny in moves:
            key = (abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [int(best[1]), int(best[2])]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        # primary: find target where we "gain tempo" over opponent
        best_gain = -10**9
        best_self = 10**9
        for rx, ry in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            gain = od - sd  # positive means we are closer than opponent
            if gain > best_gain or (gain == best_gain and sd < best_self):
                best_gain = gain
                best_self = sd
        # secondary: encourage progress toward closest contested resource, and slightly away from opponent
        opp_next = md(nx, ny, ox, oy)
        key = (-best_gain, best_self, opp_next, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]