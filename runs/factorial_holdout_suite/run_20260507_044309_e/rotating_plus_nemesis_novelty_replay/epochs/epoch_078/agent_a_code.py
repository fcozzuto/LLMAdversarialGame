def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]

    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds == 0:
            key = (10**9, 0, -0, -rx, -ry)
        else:
            # Prefer picking resources we can reach strictly earlier; otherwise reduce opponent advantage.
            diff = do - ds  # positive => we are closer in time steps
            # Break ties by favoring resources that are "less favorable" to opponent.
            extra = 0
            if ry == oy or rx == ox:
                extra = abs(ox - rx) + abs(oy - ry) - (abs(sx - rx) + abs(sy - ry))
            key = (diff, extra, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Strong preference: keep winning the race to the target; otherwise improve us while not helping opponent too much.
        diff = no - ns
        # Nudge: avoid stepping adjacent to obstacles if it doesn't help race.
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if in_bounds(px, py) and (px, py) in obstacles:
                    near_obs = 1
        mkey = (diff, -ns, -near_obs, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]