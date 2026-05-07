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

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    if not res:
        return [0, 0]
    if (sx, sy) in res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(px, py):
        best = None
        best_key = None
        for tx, ty in res:
            sd = cheb(px, py, tx, ty)
            od = cheb(ox, oy, tx, ty)
            lead = od - sd
            key = (lead, -sd, (tx + ty) & 1, -ty, -tx)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        return best

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            continue
        tx, ty = best_target(nx, ny)
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        lead = od - sd
        dist_score = -sd
        near_border = -((nx == 0) or (nx == w - 1) or (ny == 0) or (ny == h - 1))
        key = (lead, dist_score, near_border, -tx, -ty, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]