def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    target = None
    if resources:
        best = None
        for tx, ty in resources:
            d = cheb(sx, sy, tx, ty)
            oppd = cheb(ox, oy, tx, ty)
            # Prefer closer and harder for opponent; deterministic tie by (d, -oppd, tx, ty)
            key = (d, -oppd, tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        target = best[1]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if target is not None:
            val = -cheb(nx, ny, target[0], target[1])
        else:
            val = cheb(nx, ny, ox, oy)  # maximize distance from opponent
        key = val
        if best_val is None or key > best_val or (key == best_val and (dx, dy) < best_move):
            best_val = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]