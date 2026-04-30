def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs.sort()

    best = None
    if resources:
        best_key = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            key = (0 if ds <= do else 1, ds, do, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)

    tx, ty = (best if best is not None else (ox, oy))

    cur_t = dist(sx, sy, tx, ty)
    cur_o = dist(sx, sy, ox, oy)

    # Choose move that most reduces distance to target; tie-break: increases distance from opponent.
    best_move = None
    best_pair = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nt = dist(nx, ny, tx, ty)
        no = dist(nx, ny, ox, oy)
        pair = (cur_t - nt, no - cur_o, -dx, -dy)
        if best_pair is None or pair > best_pair:
            best_pair = pair
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]