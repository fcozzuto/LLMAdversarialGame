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

    best = None
    best_key = None
    for rx, ry in resources:
        k = cell_key(rx, ry)
        if best is None or k > best_key:
            best = (rx, ry)
            best_key = k

    rx, ry = best
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best_move = (0, 0)
    best_move_key = None
    for dx, dy, nx, ny in moves:
        # Primary: get closer to target; Secondary: improve race margin vs opponent; Tertiary: prefer shorter to target
        ds_now = cheb(nx, ny, rx, ry)
        ds0 = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds_now, -(ds_now), (ds0 - ds_now), -(abs(nx - ox) + abs(ny - oy)))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]