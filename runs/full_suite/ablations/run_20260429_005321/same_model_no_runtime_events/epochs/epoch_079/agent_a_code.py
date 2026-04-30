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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def manhattan(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            key = (manhattan(sx, sy, rx, ry), -manhattan(ox, oy, rx, ry), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
        best_move = None
        best_move_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (manhattan(nx, ny, tx, ty), -manhattan(nx, ny, ox, oy), dx, dy)
            if best_move_key is None or key < best_move_key:
                best_move_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]] if best_move is not None else [0, 0]

    dx0 = 0 if ox == sx else (1 if ox > sx else -1)
    dy0 = 0 if oy == sy else (1 if oy > sy else -1)
    for dx, dy in [(dx0, dy0), (dx0, 0), (0, dy0), (dx0, -dy0), (-dx0, dy0), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]