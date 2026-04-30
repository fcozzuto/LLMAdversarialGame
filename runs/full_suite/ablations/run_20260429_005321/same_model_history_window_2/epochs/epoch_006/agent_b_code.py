def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def neigh_block(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            score = (opd - myd) * 10 - neigh_block(rx, ry)
            if best is None or score > best[0] or (score == best[0] and (rx, ry) < best[1]):
                best = (score, (rx, ry))
        if best is None:
            tx, ty = w // 2, h // 2
        else:
            tx, ty = best[1]
    else:
        tx, ty = w // 2, h // 2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        val = (myd2, -opd2, neigh_block(nx, ny), dx, dy)
        if best_move is None or val < best_move[0]:
            best_move = (val, (dx, dy))

    if best_move is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [best_move[1][0], best_move[1][1]]