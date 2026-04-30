def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    if resources:
        best_t = None
        best_s = -10**18
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - sd
            s = lead * 10 - sd - (od // 4)
            if s > best_s:
                best_s = s
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_u = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        new_lead = od - nd
        utility = new_lead * 10 - nd
        # Small deterministic tie-break: prefer moves that move closer in straight-ish ways
        utility -= (abs(nx - tx) + abs(ny - ty)) // 8
        if utility > best_u:
            best_u = utility
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]