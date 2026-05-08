def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_res = None
    best_key = None
    if resources:
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            key = (do - ds, -ds, -rx, -ry)
            if best_key is None or key > best_key:
                best_key, best_res = key, (rx, ry)

    if best_res is None:
        return [0, 0]

    tx, ty = best_res

    def step_toward(curx, cury, targetx, targety, dx, dy):
        nx, ny = curx + dx, cury + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            return None
        return nx, ny

    candidates = []
    for dx, dy in moves:
        nxt = step_toward(sx, sy, tx, ty, dx, dy)
        if nxt is None:
            continue
        nx, ny = nxt
        dsn = man(nx, ny, tx, ty)
        don = man(ox, oy, tx, ty)
        adv = don - dsn  # positive means we are closer than opponent to the same target
        # also consider whether this move creates a strong alternative by moving closer to any resource
        alt = 0
        if resources:
            for r in resources:
                if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                    continue
                rx, ry = int(r[0]), int(r[1])
                if not inb(rx, ry) or (rx, ry) in obs:
                    continue
                dsn2 = man(nx, ny, rx, ry)
                do2 = man(ox, oy, rx, ry)
                k = do2 - dsn2
                if k > alt:
                    alt = k
        score = (adv, alt, -dsn, -(nx - tx) * (nx - tx) - (ny - ty) * (ny - ty))
        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True, key=lambda t: t[0])
    return [int(candidates[0][1]), int(candidates[0][2])]