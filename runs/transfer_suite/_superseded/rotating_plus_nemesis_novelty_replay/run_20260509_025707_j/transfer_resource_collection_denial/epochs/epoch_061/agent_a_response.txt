def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    valid_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    best_target = None  # predicted opponent target: min opp distance, tie: min resource x then y
    best_od = None
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        od = man(ox, oy, rx, ry)
        key = (od, rx, ry)
        if best_target is None or key < (best_od, best_target[0], best_target[1]):
            best_target = (rx, ry)
            best_od = od

    tx, ty = best_target if best_target is not None else (sx, sy)

    best = None  # lexicographic: (max_adv, target_adv, -self_best_dist, self_dist_to_pred, dx, dy)
    for dx, dy, nx, ny in valid_moves:
        max_adv = None
        self_best_dist = None
        target_sd = man(nx, ny, tx, ty)
        target_adv = man(ox, oy, tx, ty) - target_sd
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            if max_adv is None or adv > max_adv or (adv == max_adv and sd < self_best_dist):
                max_adv = adv
                self_best_dist = sd

        key = (max_adv, target_adv, -self_best_dist if self_best_dist is not None else 0, target_sd)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]