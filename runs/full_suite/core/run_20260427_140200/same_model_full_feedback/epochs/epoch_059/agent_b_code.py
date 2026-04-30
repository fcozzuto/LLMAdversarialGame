def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def best_cell_for_resource(tx, ty):
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = cheb(nx, ny, tx, ty)
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return best[1] if best else (0, 0)

    if resources:
        tx, ty = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
        return best_cell_for_resource(tx, ty)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me = cheb(nx, ny, ox, oy)
        d_op = cheb(ox, oy, sx, sy)
        gain = d_op - d_me
        if best is None or gain > best[0] or (gain == best[0] and (dx, dy) < best[1]):
            best = (gain, (dx, dy))
    return best[1] if best else [0, 0]