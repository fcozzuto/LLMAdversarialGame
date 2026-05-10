def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = int(observation.get("turns_remaining", 0))

    obs = set((int(x), int(y)) for x, y in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res_list = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obs:
            res_list.append((rx, ry))

    if not res_list:
        return [0, 0]

    # Pick a target resource: maximize how much closer we are than opponent.
    best_t = None
    best_k = (-10**18, -10**18, -10**18)
    for rx, ry in res_list:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        k = (od - sd, -sd, -od)  # prefer winning it sooner; then closer; then deny
        if k > best_k:
            best_k = k
            best_t = (rx, ry)

    tx, ty = best_t

    # Choose move by maximizing expected advantage for collecting target, with small extra term for any resource.
    best_m = (0, 0)
    best_mk = (-10**18, -10**18, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd_t = cheb(nx, ny, tx, ty)
        od_t = cheb(ox, oy, tx, ty)
        adv = od_t - sd_t
        # add modest reward for approaching any resource (keeps behavior robust)
        close_bonus = 0
        for rx, ry in res_list:
            d = cheb(nx, ny, rx, ry)
            if d == 0:
                close_bonus += 5
            else:
                close_bonus += 1.0 / (1 + d)
        # Deterministic tie-break: prefer moves that reduce distance to opponent less (deny) when tied.
        deny = -cheb(ox, oy, nx, ny)
        k1 = adv
        k2 = -sd_t
        k3 = deny
        # incorporate close_bonus deterministically via scaled integer
        k4 = int(close_bonus * 10 + (turns_remaining % 7))
        key = (k1, k2, k3, k4)
        if key > best_mk:
            best_mk = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]