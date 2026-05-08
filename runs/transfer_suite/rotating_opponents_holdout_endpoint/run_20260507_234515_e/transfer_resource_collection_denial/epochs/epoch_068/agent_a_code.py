def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a resource we can secure earlier than the opponent.
    best_t = None
    best_key = None
    for rx, ry in res:
        dS = man(sx, sy, rx, ry)
        dO = man(ox, oy, rx, ry)
        # Advantage favors us being closer; tie-break favors lower dS.
        # Small preference for resources that are "on our half" vs opponent.
        half_bias = 0
        if sx <= (w - 1) / 2:
            half_bias = -1 if rx <= (w - 1) / 2 else 0
        else:
            half_bias = -1 if rx >= (w - 1) / 2 else 0
        key = (dS - dO, dS, -half_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Prefer stepping that reduces distance to target, while not allowing opponent to be safer.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ndS = man(nx, ny, tx, ty)
        ndO = man(ox, oy, tx, ty)
        # If we are already close to the target, don't get baited too far away.
        proximity_bonus = -ndS
        mkey = (ndS - ndO, ndS, proximity_bonus, nx, ny)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]