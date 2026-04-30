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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    if not valid(sx, sy):
        for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = w // 2, h // 2

    if resources:
        best = None
        best_key = -10**9
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            key = (oppd - myd) * 1000 - myd  # deterministic tiebreak
            if key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = cx, cy

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        val = -d * 10
        if resources:
            od = cheb(ox, oy, tx, ty)
            val += (od - d)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]