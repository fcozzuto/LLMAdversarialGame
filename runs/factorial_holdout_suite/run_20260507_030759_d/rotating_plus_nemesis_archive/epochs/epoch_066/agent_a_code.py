def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy  # Chebyshev

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    tx, ty = sx, sy
    if resources:
        best = None
        for x, y in resources:
            sd = dist(sx, sy, x, y)
            od = dist(ox, oy, x, y)
            score = (od - sd, -sd, x, y)
            if best is None or score > best:
                best = score
                tx, ty = x, y
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    best_move = None
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        d = dist(nx, ny, tx, ty)
        # Prefer moves that reduce distance; tie-break deterministically by dx,dy
        key = (d, abs(dx) + abs(dy), dx, dy)
        if best_move is None or key < best_d:
            best_d = key
            best_move = (dx, dy)

    if best_move is not None:
        return [best_move[0], best_move[1]]
    return [0, 0]