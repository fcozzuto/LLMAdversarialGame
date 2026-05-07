def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def cell_key(cx, cy):
        ds = cheb(sx, sy, cx, cy)
        do = cheb(ox, oy, cx, cy)
        return (do - ds, -ds)

    best_rx, best_ry = resources[0]
    best_key = cell_key(best_rx, best_ry)
    for rx, ry in resources[1:]:
        k = cell_key(rx, ry)
        if k > best_key:
            best_key, best_rx, best_ry = k, rx, ry

    tx, ty = best_rx, best_ry

    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            nds = cheb(nx, ny, tx, ty)
            ddo = cheb(nx, ny, ox, oy)
            score = ( -nds, ddo, -abs(nx - tx) - abs(ny - ty) )
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move