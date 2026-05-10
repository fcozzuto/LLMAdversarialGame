def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res_list = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obs:
            res_list.append((rx, ry))
    if not res_list:
        return [0, 0]

    # Bias away from resources with opponent-aligned row (helps vs sweep_rows-like behavior).
    best_t = None
    best = (-10**18, -10**18, -10**18)
    for rx, ry in res_list:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        row_mismatch = 0 if ry == oy else 1  # if opponent likely sweeps a row, mismatch is harder
        effective_od = od + row_mismatch
        adv = effective_od - sd
        # tie-break: prefer closer, then bigger deny (anti-opponent), then deterministic by coordinates
        k = (adv, -sd, -effective_od, -rx, -ry)
        if k > best:
            best = k
            best_t = (rx, ry)

    tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_m = (-10**18, -10**18, -10**18)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty) + (0 if ty == oy else 1)
        score = (opd - myd, -myd, -opd, -nx, -ny)
        if score > best_m:
            best_m = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]