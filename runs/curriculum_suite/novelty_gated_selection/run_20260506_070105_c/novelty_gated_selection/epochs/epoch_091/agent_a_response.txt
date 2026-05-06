def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def edge_bias(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    # Choose target:
    # - If any resource we can reach at least as fast as opponent, take the best one.
    # - Otherwise, move to a "cut" cell near the midpoint and slightly closer to opponent.
    my_best = None
    my_best_key = None
    for rx, ry in resources:
        dm = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - dm  # positive if we are closer or tied
        if adv >= 0:
            key = (-(adv), -edge_bias(rx, ry), dm, rx, ry)
            if my_best_key is None or key < my_best_key:
                my_best_key = key
                my_best = (rx, ry)

    if my_best is not None:
        tx, ty = my_best
    else:
        mx = (sx + ox) // 2
        my = (sy + oy) // 2
        # deterministically prefer the step direction toward opponent in order to cut off
        step_x = 0 if ox == mx else (1 if ox > mx else -1)
        step_y = 0 if oy == my else (1 if oy > my else -1)
        tx, ty = mx + step_x, my + step_y
        tx = min(w - 1, max(0, tx))
        ty = min(h - 1, max(0, ty))
        # if invalid (on obstacle), fall back to nearer midpoint
        if (tx, ty) in obstacles:
            tx, ty = mx, my
            tx = min(w - 1, max(0, tx))
            ty = min(h - 1, max(0, ty))
            if (tx, ty) in obstacles:
                tx, ty = sx, sy

    # One-step obstacle-aware greedy selection maximizing (we approach target while reducing opponent advantage).
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        dm2 = dist(nx, ny, tx, ty)
        do2 = dist(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; if we can't, prefer moves that increase closeness relative to opponent.
        adv2 = do2 - dm2
        key = (dm2, -adv2, -edge_bias(nx, ny), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]