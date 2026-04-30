def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, x2, y2):
        dx = a - x2
        if dx < 0:
            dx = -dx
        dy = b - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = [d for d in dirs if inside(sx + d[0], sy + d[1])]

    if not resources:
        best = (None, -1e9)
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            score = dist(nx, ny, ox, oy)
            if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
                best = ((dx, dy), score)
        return list(best[0])

    best_res = None
    best_key = None
    for x, y in resources:
        dme = dist(sx, sy, x, y)
        dop = dist(ox, oy, x, y)
        if dme <= dop:
            key = (dme, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best_res = (x, y)

    if best_res is None:
        best = (None, -1e9)
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            score = dist(nx, ny, ox, oy)
            if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
                best = ((dx, dy), score)
        return list(best[0])

    tx, ty = best_res
    best_move = None
    best_val = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        val = (dist(nx, ny, tx, ty), abs((nx - ox)) + abs((ny - oy)))
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]