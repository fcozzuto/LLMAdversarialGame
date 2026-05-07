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
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist((sx, sy), (rx, ry))
        op_d = dist((ox, oy), (rx, ry))
        key = (op_d - my_d, -my_d, -abs(rx - rx))  # primary: maximize lead; secondary: closer
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if dx != 0 and ((tx - sx) == 0):
            pass
        nd = dist((nx, ny), (tx, ty))
        # Prefer stepping closer while keeping opponent from landing immediately on same resource region
        my_to_res = nd
        op_to_res = dist((ox, oy), (tx, ty))
        key = (-my_to_res, (op_to_res - my_to_res), -((nx - tx) ** 2 + (ny - ty) ** 2))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]