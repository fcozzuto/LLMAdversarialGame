def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_cell = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - sd  # positive means we are closer
        near_op = -cheb(ox, oy, rx, ry)  # discourage letting denier steal
        row_bias = -(abs(ry - sy))      # keep line progress deterministic
        key = (advantage, row_bias, near_op, -(sd), -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (rx, ry)

    tx, ty = best_cell
    best_move = [0, 0]
    best_mkey = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Re-score target choice locally by advantage to reduce detours
        # and avoid moving into "opponent-snap" positions.
        min_adv = -10**9
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                pass
            sd2 = cheb(nx, ny, rx, ry)
            od2 = cheb(ox, oy, rx, ry)
            adv2 = od2 - sd2
            if adv2 < min_adv:
                continue
            if adv2 > min_adv:
                min_adv = adv2
        key = (min_adv, -d, -(abs(nx - tx) + abs(ny - ty)), -cheb(ox, oy, nx, ny), -cheb(ox, oy, tx, ty))
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_move = [mx, my]

    return [int(best_move[0]), int(best_move[1])]