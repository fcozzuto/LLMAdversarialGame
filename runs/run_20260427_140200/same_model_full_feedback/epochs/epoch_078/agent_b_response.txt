def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    if resources:
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # prefer resources I'm relatively closer to than opponent; tie-break by my distance, then position
            key = (myd - opd, myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                target = (rx, ry)

    if target is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = target

    if sx == tx and sy == ty:
        bestm = (0, 0)
    else:
        desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
        desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

        best_key = None
        bestm = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # prefer moves that progress toward target, then align with desired direction, and avoid getting closer to opponent
            opp_after = cheb(nx, ny, ox, oy)
            align = abs(dx - desired_dx) + abs(dy - desired_dy)
            key = (d, align, -opp_after, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                bestm = (dx, dy)

    dx, dy = bestm
    return [int(dx), int(dy)]