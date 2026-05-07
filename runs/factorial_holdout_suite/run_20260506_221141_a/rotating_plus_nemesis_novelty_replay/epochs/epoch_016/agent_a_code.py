def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    def mindist_adv(x, y):
        best_min = -10**9
        best_ds = 10**9
        for rx, ry in res:
            ds = abs(rx - x) + abs(ry - y)
            do = abs(rx - ox) + abs(ry - oy)
            adv = do - ds
            if adv < best_min:
                best_min = adv
            if ds < best_ds:
                best_ds = ds
        return best_min, best_ds

    best_move = (0, 0)
    best_val = -10**18
    best_tie = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        adv_min, ds_min = mindist_adv(nx, ny)
        val = adv_min
        if val > best_val or (val == best_val and ds_min < best_tie):
            best_val = val
            best_tie = ds_min
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]