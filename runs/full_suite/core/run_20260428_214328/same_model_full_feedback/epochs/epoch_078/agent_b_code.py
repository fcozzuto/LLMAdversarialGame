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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_dx, best_dy, best_val = 0, 0, None
    target = None
    if resources:
        best_res = None
        best_dist = None
        for x, y in resources:
            d = abs(sx - x) + abs(sy - y)
            if best_dist is None or d < best_dist or (d == best_dist and (x, y) < best_res):
                best_dist, best_res = d, (x, y)
        target = best_res

    tx, ty = (w - 1) // 2, (h - 1) // 2
    if target is not None:
        tx, ty = target

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_t = abs(nx - tx) + abs(ny - ty)
        d_to_o = abs(nx - ox) + abs(ny - oy)
        val = d_to_t - 0.1 * d_to_o
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = val
            best_dx, best_dy = dx, dy

    if ok(sx + best_dx, sy + best_dy):
        return [best_dx, best_dy]
    return [0, 0]