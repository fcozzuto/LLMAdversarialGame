def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return [0 if sx == tx else (1 if tx > sx else -1), 0 if sy == ty else (1 if ty > sy else -1)]

    for r in resources:
        if (sx, sy) == (r[0], r[1]):
            return [0, 0]

    best_r = None
    best_key = None  # (adv, -self_d, opp_d)
    for r in resources:
        rx, ry = r[0], r[1]
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        adv = opp_d - self_d
        key = (adv, -self_d, opp_d)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    cur_tdist = cheb(sx, sy, tx, ty)

    def neighbor_open(nx, ny):
        cnt = 0
        for dx, dy in moves:
            x, y = nx + dx, ny + dy
            if inb(x, y):
                cnt += 1
        return cnt

    best_move = (0, 0)
    best_move_key = None  # (tdist, -open, tie by dx,dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        tdist = cheb(nx, ny, tx, ty)
        open_ct = neighbor_open(nx, ny)
        key = (tdist, -open_ct, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    if best_move_key is None:
        return [0, 0]

    # If we can’t improve target distance, make a deterministic sidestep to increase mobility.
    if best_move_key[0] >= cur_tdist:
        best_mob = None
        best_mb = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            open_ct = neighbor_open(nx, ny)
            tdist = cheb(nx, ny, tx, ty)
            key = (-open_ct, tdist, dx, dy)
            if best_mob is None or key < best_mob:
                best_mob = key
                best_mb = (dx, dy)
        return [best_mb[0], best_mb[1]]

    return [best_move[0], best_move[1]]