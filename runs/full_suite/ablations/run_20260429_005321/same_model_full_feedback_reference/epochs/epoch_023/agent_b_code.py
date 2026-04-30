def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            key = (sd - od, sd, -(rx + ry))  # prefer where we are not behind; then closer
            if best_key is None or key < best_key:
                best_key, best_r = key, (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (w - 1 if sx < w // 2 else 0), (h - 1 if sy < h // 2 else 0)

    best_move = (0, 0)
    best_val = None
    order = sorted(dirs, key=lambda d: (d[0], d[1]))  # deterministic tie-break
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist_next = md(nx, ny, tx, ty)
        opp_next = md(nx, ny, ox, oy)
        val = (-dist_next * 10) + (opp_next)  # primarily minimize distance to target, then maximize separation
        if best_val is None or val > best_val:
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]