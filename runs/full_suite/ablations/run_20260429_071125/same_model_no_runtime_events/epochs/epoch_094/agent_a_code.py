def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        bestkey = None
        for tx, ty in resources:
            d_me = cheb(sx, sy, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # Prefer taking/contesting advantage, then closer
            key = (d_op - d_me, -d_me, -(tx == sx and ty == sy))
            if bestkey is None or key > bestkey:
                bestkey = key
                best = (tx, ty)
        tx, ty = best
        bestmv = None
        bestkey = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_me = cheb(nx, ny, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # Reduce our distance; keep/extend contest lead; avoid standing still if possible
            key = (d_op - d_me, -d_me, -abs(nx - tx) - abs(ny - ty), -((dx == 0 and dy == 0)))
            if bestkey is None or key > bestkey:
                bestkey = key
                bestmv = (dx, dy)
        if bestmv is None:
            return [0, 0]
        return [int(bestmv[0]), int(bestmv[1])]

    # No resources: move to increase distance from opponent while keeping towards center
    cx, cy = (w - 1) // 2, (h - 1) // 2
    bestmv = None
    bestkey = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        k = (cheb(nx, ny, ox, oy), -cheb(nx, ny, cx, cy), -((dx == 0 and dy == 0)))
        if bestkey is None or k > bestkey:
            bestkey = k
            bestmv = (dx, dy)
    if bestmv is None:
        return [0, 0]
    return [int(bestmv[0]), int(bestmv[1])]