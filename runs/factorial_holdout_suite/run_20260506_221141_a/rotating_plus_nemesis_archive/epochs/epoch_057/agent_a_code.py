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

    def mdist(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = mdist((sx, sy), (rx, ry))
        op_d = mdist((ox, oy), (rx, ry))
        lead = op_d - my_d
        key = (lead, -my_d, -(rx * 997 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    options = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = mdist((nx, ny), (tx, ty))
            opp_d = mdist((ox, oy), (tx, ty))
            val = (opp_d - d, -d, dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
    return [best_move[0], best_move[1]]