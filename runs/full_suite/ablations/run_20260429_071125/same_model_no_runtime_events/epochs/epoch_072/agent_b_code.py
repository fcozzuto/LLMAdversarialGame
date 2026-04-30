def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # obstacle "pressure" around a cell
    def obst_adj(x, y):
        c = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                if (x + ix, y + iy) in obstacles:
                    c += 1
        return c

    best = None
    best_val = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets where we are earlier; also prefer safer/closer.
        val = (do - ds) * 10.0 - ds * 0.8 - obst_adj(rx, ry) * 2.0
        # If tied, slightly prefer cells closer to center to reduce dead-ends.
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        val -= 0.05 * (abs(rx - cx) + abs(ry - cy))
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = (0, 0)
    bestmv = -10**9
    curd = cheb(sx, sy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # if we don't get closer, still allow if it improves safety or blocks opponent
        do_now = cheb(ox, oy, tx, ty)
        # potential improvement: reduce our distance; also slightly increase opponent distance to same target
        mv = (curd - nd) * 8.0 + (do_now - cheb(ox, oy, tx, ty)) * 0.0
        mv -= obst_adj(nx, ny) * 1.5
        mv -= 0.02 * (abs(nx - (w - 1)) + abs(ny - (h - 1)))  # minor direction stability
        if mv > bestmv:
            bestmv = mv
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]