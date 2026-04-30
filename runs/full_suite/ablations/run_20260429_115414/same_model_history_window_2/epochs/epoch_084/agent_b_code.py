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

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    if resources:
        best_dist = 10**18
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < best_dist:
                best_dist = d
        targets = [(rx, ry) for (rx, ry) in resources if cheb(sx, sy, rx, ry) == best_dist]
        tx, ty = min(targets, key=lambda p: (p[0], p[1]))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            val = -d
            if (nx, ny) in resources:
                val += 1000000
            if val > best_score or (val == best_score and (dx, dy) < best_move):
                best_score = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: maximize distance to opponent (and prefer staying legal with deterministic tie-break)
    best_d = -1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if d > best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]