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
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick best target by race advantage (self arrives earlier); then closer for tie-break.
    best_t = None
    best_score = None
    for rx, ry in resources:
        sd = d((sx, sy), (rx, ry))
        od = d((ox, oy), (rx, ry))
        # Higher is better
        score = (od - sd, -(sd), rx, ry)
        if best_score is None or score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    best_m = None
    best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = d((nx, ny), (tx, ty))
        nod = d((ox, oy), (tx, ty))
        # Prefer making our race as large as possible; also avoid drifting from target.
        v = (nod - nsd, -nsd, -abs(nx - tx) - abs(ny - ty), -abs(nx - sx) - abs(ny - sy))
        if best_v is None or v > best_v:
            best_v = v
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]