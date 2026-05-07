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
        return dx if dx > dy else dy  # Chebyshev for 8-direction moves

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist((sx, sy), (rx, ry))
        op_d = dist((ox, oy), (rx, ry))
        lead = op_d - my_d  # positive: we are closer
        total = my_d + op_d
        key = (lead, -total, -my_d, -(abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)))
        if best is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        my_d = dist((nx, ny), (tx, ty))
        op_d = dist((ox, oy), (tx, ty))
        lead = op_d - my_d
        val = (lead, -my_d, -(abs(tx - nx) + abs(ty - ny)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]