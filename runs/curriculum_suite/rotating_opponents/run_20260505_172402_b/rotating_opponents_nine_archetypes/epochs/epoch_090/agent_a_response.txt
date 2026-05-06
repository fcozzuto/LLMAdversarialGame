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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    if not valid(sx, sy):
        for y in range(h):
            for x in range(w):
                if valid(x, y):
                    sx, sy = x, y
                    break
            else:
                continue
            break

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        dx = 0 if ox == sx else (-1 if ox > sx else 1)
        dy = 0 if oy == sy else (-1 if oy > sy else 1)
        tx, ty = sx + dx, sy + dy
        if valid(tx, ty):
            return [dx, dy]
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def dist(a, b, x, y):
        return abs(a - x) + abs(b - y)

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_r_val = None
        for rx, ry in resources:
            du = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            diag = abs((nx - rx) - (ny - ry))
            v = du - 0.95 * do + 0.02 * diag  # prioritize targets opponent is less able to reach
            if best_r_val is None or v < best_r_val:
                best_r_val = v
        if best_val is None or best_r_val < best_val:
            best_val = best_r_val
            best_move = [dx, dy]

    return best_move