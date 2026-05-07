def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = observation.get("resources") or []
    best = None
    best_val = 10**9
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2): 
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inside(rx, ry) and (rx, ry) not in obst:
            continue
        if (rx, ry) in obst: 
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = ds - 0.95 * do
        if val < best_val:
            best_val = val
            best = (rx, ry)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if best is None:
        # No known resources: move to increase distance from opponent while feasible.
        best_move = (0, 0)
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            score = cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    rx, ry = best
    best_move = (0, 0)
    best_score = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = ds - 0.95 * do
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]