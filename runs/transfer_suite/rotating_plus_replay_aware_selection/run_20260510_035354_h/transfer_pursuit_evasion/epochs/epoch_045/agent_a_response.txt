def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("evader" in self_role)
    if ("evad" in opp_role) or ("evader" in opp_role):
        self_evader = False
    elif ("purs" in self_role):
        self_evader = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def score(nx, ny):
        d = dist((nx, ny), (ox, oy))
        # discourage stepping into obstacles (shouldn't happen) and prefer central-ish squares deterministically
        center_bias = -0.01 * (abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny))
        if self_evader:
            # maximize distance; also lightly penalize boundary crowding
            boundary_pen = -0.02 * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
            return (d, boundary_pen, center_bias)
        else:
            # minimize distance; also avoid getting stuck against obstacles
            return (-d, center_bias)

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        sc = score(nx, ny)
        if best is None or (sc > best if self_evader else sc > best):
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]