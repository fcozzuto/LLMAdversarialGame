def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than the opponent; break ties by shorter ds then fixed order.
            key = (-(do - ds), ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
        # Greedy step: choose valid move that most reduces Chebyshev distance to target.
        curd = cheb(sx, sy, tx, ty)
        best_move = [0, 0]
        best_newd = curd
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = cheb(nx, ny, tx, ty)
            if nd < best_newd or (nd == best_newd and (dx, dy) < (best_move[0], best_move[1])):
                best_newd = nd
                best_move = [dx, dy]
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: shift toward opponent to contest space, but avoid obstacles.
    # Use deterministic "press" direction: move to decrease chebyshev distance to opponent.
    curd = cheb(sx, sy, ox, oy)
    best_move = [0, 0]
    best_newd = curd
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, ox, oy)
        if nd < best_newd or (nd == best_newd and (dx, dy) < (best_move[0], best_move[1])):
            best_newd = nd
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]