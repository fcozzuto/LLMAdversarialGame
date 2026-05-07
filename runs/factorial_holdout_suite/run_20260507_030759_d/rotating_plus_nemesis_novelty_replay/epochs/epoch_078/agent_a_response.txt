def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = (-10**9, -10**9, -10**9)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Counter sweep_rows: prioritize resources that differ strongly in row/column from opponent,
        # but still race if we can arrive earlier.
        rowcol = abs(ry - oy) - abs(rx - ox)
        center = -(abs(rx - cx) + abs(ry - cy))
        key = (do - ds, -ds, rowcol * 0.01 + center * 0.001)
        if key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    prefer = (0, 0)
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    prefer = (dx, dy)

    best_move = prefer if valid(sx + prefer[0], sy + prefer[1]) else (0, 0)
    best_dist = 10**9
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        # Deterministic: minimize remaining cheb distance; tie by dx then dy.
        d = cheb(nx, ny, tx, ty)
        if d < best_dist or (d == best_dist and (ddx, ddy) < best_move):
            best_dist = d
            best_move = (ddx, ddy)
    return [int(best_move[0]), int(best_move[1])]