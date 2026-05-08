def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in res:
        sd = man(sx, sy, tx, ty)
        td = man(ox, oy, tx, ty)
        dx0 = abs(tx - sx)
        dy0 = abs(ty - sy)
        key = (td - sd, -sd, -(dx0 + dy0), -(tx + ty), -tx)
        if best_key is None or key > best_key:
            best_key, best = key, (tx, ty)
    tx, ty = best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_mkey = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer moves that reduce our distance to the target while also not becoming worse than opponent
        mkey = (-(nd - sd), -(od - nd), -nd, -(abs(tx - nx) + abs(ty - ny)), -dx, -dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    return best_move