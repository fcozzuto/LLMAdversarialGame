def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < int(w) and 0 <= y < int(h):
                blocked.add((x, y))

    def free(x, y):
        return 0 <= x < int(w) and 0 <= y < int(h) and (x, y) not in blocked

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    if resources:
        best = None
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if best is None or d < best[0] or (d == best[0] and (x, y) < (best[1], best[2])):
                best = (d, x, y)
        tx, ty = best[1], best[2]
        if sx == tx and sy == ty:
            return [0, 0]
        best_move = None
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if best_move is None or d < best_d or (d == best_d and (dx, dy) < best_move):
                best_move = (dx, dy)
                best_d = d
        return [int(best_move[0]), int(best_move[1])] if best_move is not None else [0, 0]

    # No resources: keep distance from opponent
    best_move = None
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if best_move is None or d > best_d or (d == best_d and (dx, dy) < best_move):
            best_move = (dx, dy)
            best_d = d
    return [int(best_move[0]), int(best_move[1])] if best_move is not None else [0, 0]