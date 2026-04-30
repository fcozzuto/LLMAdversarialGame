def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    x, y = int(x), int(y)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if resources and (x, y) in set(resources):
        return [0, 0]

    if resources:
        target = None
        best = None
        for tx, ty in resources:
            ds = cheb(x, y, tx, ty)
            do = cheb(ox, oy, tx, ty)
            key = (ds - do, ds, tx, ty)
            if best is None or key < best:
                best = key
                target = (tx, ty)
    else:
        target = (0, 0) if (x + y) > (w - 1 + h - 1) / 2 else (w - 1, h - 1)

    tx, ty = target
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        d_to_res = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        on_res = 1 if (nx, ny) == (tx, ty) else 0
        score = (on_res * 100000) + (-d_to_res * 10) + (d_to_opp)  # primary: reach target, secondary: stay away
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]