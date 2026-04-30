def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if legal(x, y):
                resources.append((x, y))

    def cheb(x, y, tx, ty):
        dx = x - tx
        if dx < 0:
            dx = -dx
        dy = y - ty
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    tx, ty = ox, oy
    if resources:
        best = None
        best_key = None
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            key = (do <= ds, ds, -do, x, y)  # prefer resource we can reach first (or tie), then closest, then deterministic
            if best_key is None or key > best_key:
                best_key = key
                best = (x, y)
        tx, ty = best

    if (tx, ty) == (sx, sy) and not resources:
        tx, ty = (w // 2, h // 2)

    best_move = None
    best_dist = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        if best_dist is None or dist < best_dist or (dist == best_dist and (dx, dy) < best_move):
            best_dist = dist
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move is not None else [0, 0]