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

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for rx, ry in resources:
        self_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        key = (opp_d - self_d, -self_d, rx, ry)
        if best is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd_self = md(nx, ny, tx, ty)
        nd_opp = md(ox, oy, tx, ty)
        k = (-nd_opp, -((nd_self == 0) * 100000 + 0), -nd_self, dx, dy)
        if best_m is None or k > best_k:
            best_k = k
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]