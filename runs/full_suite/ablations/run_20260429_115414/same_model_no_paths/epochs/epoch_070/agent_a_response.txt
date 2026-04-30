def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obst_adj_pen(x, y):
        p = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in obstacles:
                    p += 1
        if x == 0 or x == w - 1:
            p += 1
        if y == 0 or y == h - 1:
            p += 1
        return p

    if not resources:
        return [0, 0]

    best_t = resources[0]
    best_sc = -10**9
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        sc = (opd - myd) * 10 - myd + opd * 0.2
        if sc > best_sc:
            best_sc, best_t = sc, (rx, ry)

    tx, ty = best_t
    move_opts = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cur_myd = cheb(sx, sy, tx, ty)
    chosen = (0, 0)
    chosen_val = -10**18

    for dx, dy in move_opts:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Value: prioritize getting closer to target; if opponent is also close, try to deny by reducing their edge.
        oppd = cheb(ox, oy, tx, ty)
        my_edge = oppd - nd
        val = my_edge * 10 - nd - obst_adj_pen(nx, ny) * 0.6
        # If we're about to be overtaken, prefer moves that change parity/avoid staying still.
        if myd := cur_myd:
            if nd >= myd and (cheb(ox, oy, nx, ny) <= oppd):
                val -= 3
        if val > chosen_val:
            chosen_val, chosen = val, (dx, dy)
        elif val == chosen_val:
            if (dx, dy) < chosen:
                chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]