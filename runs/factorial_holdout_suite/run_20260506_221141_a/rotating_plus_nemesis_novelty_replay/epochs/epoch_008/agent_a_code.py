def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    def best_for_pos(nx, ny):
        bestv = -10**9
        best_tie = 10**9
        for rx, ry in res:
            myd = abs(nx - rx) + abs(ny - ry)
            if myd == 0:
                return 10**8
            # opponent "sweep rows" prediction: keep y, move x toward target (one step)
            oxp = ox + (1 if rx > ox else -1 if rx < ox else 0)
            opd_pred = abs(oxp - rx) + abs(oy - ry)
            v = (opd_pred - myd) - 2 * myd
            if v > bestv or (v == bestv and myd < best_tie):
                bestv = v
                best_tie = myd
        return bestv

    best_move = (0, 0)
    best_val = -10**18
    best_dist = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = best_for_pos(nx, ny)
        d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
        if v > best_val or (v == best_val and d < best_dist):
            best_val, best_dist = v, d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]