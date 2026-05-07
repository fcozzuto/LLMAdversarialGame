def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x2 - x1) + abs(y2 - y1)

    best = None
    best_key = None
    for rx, ry in resources:
        d_self = manh(sx, sy, rx, ry)
        d_op = manh(ox, oy, rx, ry)
        lead = d_op - d_self
        key = (-lead, d_self, abs(rx - (w - 1)), abs(ry - (h - 1)))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    dxs = -1 if tx < sx else (1 if tx > sx else 0)
    dys = -1 if ty < sy else (1 if ty > sy else 0)
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dist = manh(nx, ny, tx, ty)
                candidates.append((dist, abs(dx - dxs) + abs(dy - dys), dx, dy))
    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]