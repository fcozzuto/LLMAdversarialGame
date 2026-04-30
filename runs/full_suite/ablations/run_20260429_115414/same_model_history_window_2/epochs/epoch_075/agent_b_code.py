def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_val = -10**18
    best_move = [0, 0]

    if resources:
        target_list = resources
    else:
        target_list = [(cx, cy)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_self = min(cheb(nx, ny, tx, ty) for tx, ty in target_list)
        val = -d_self + 0.35 * d_opp
        if resources and (nx, ny) in resources:
            val += 1000
        if (not resources) and cheb(nx, ny, cx, cy) < cheb(sx, sy, cx, cy):
            val += 10
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    if not (best_move[0] == 0 and best_move[1] == 0):
        return best_move
    if ok(sx, sy):
        return [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
    return [0, 0]