def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if not resources:
        # Deterministic fallback: move away from opponent (or toward center if aligned)
        best = None
        bestv = (-10**9, 10**9)
        for dx, dy, nx, ny in legal:
            v = man(nx, ny, ox, oy)
            t = abs((nx - (w - 1) / 2.0)) + abs((ny - (h - 1) / 2.0))
            key = (v, -t)
            if key > bestv:
                bestv = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose a target resource where we have an earlier arrival advantage.
    my_best = None
    best_adv = -10**9
    best_m = 10**9
    best_ox = 10**9
    for rx, ry in resources:
        dm = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - dm  # positive means I'm closer
        if adv > best_adv or (adv == best_adv and (dm < best_m or (dm == best_m and do < best_ox))):
            best_adv = adv
            best_m = dm
            best_ox = do
            my_best = (rx, ry)

    # If no advantage, just go for closest resource to us (still deterministic).
    if best_adv <= 0:
        dm0 = 10**9
        for rx, ry in resources:
            dm = man(sx, sy, rx, ry)
            if dm < dm0 or (dm == dm0 and (rx, ry) < my_best):
                dm0 = dm
                my_best = (rx, ry)

    tx, ty = my_best

    # Among legal moves, minimize distance to target; tie-break: maximize distance from opponent.
    best_move = (0, 0)
    best_key = (10**9, -10**9, 10**9)  # (dist_to_target, -opp_dist, dx,dy order via final)
    for dx, dy, nx, ny in legal:
        d_to = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        key = (d_to, -d_opp, dx * 10 + dy)  # deterministic tie-break
        if key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]