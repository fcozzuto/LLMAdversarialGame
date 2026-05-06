def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res.append((x, y))

    def dist(a, b, c, d):
        x = a - c
        y = b - d
        return x * x + y * y

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not res:
        tx = 1 if sx < cx else -1 if sx > cx else 0
        ty = 1 if sy < cy else -1 if sy > cy else 0
        if tx == 0 and ty == 0:
            return [0, 0]
        candidates = []
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((-(nx - cx) * (nx - cx) - (ny - cy) * (ny - cy), dx, dy))
        candidates.sort(reverse=True)
        return [int(candidates[0][1]), int(candidates[0][2])] if candidates else [0, 0]

    opp_best = 10**18
    for rx, ry in res:
        opp_best = min(opp_best, dist(ox, oy, rx, ry))

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        self_best = 10**18
        for rx, ry in res:
            self_best = min(self_best, dist(nx, ny, rx, ry))
        # Prefer moves that reduce our distance to resources; slightly prefer making opponent's closest resource farther.
        val = -self_best + 0.001 * opp_best
        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])] if best is not None else [0, 0]