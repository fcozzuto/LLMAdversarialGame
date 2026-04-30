def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if resources:
        tx, ty = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
    else:
        tx, ty = ox, oy

    best = (10**18, 10**18, None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_t = abs(nx - tx) + abs(ny - ty)
        d_to_o = abs(nx - ox) + abs(ny - oy)
        score = (d_to_t, -d_to_o)
        if score < (best[0], best[1]):
            best = (score[0], score[1], (dx, dy))

    if best[2] is None:
        return [0, 0]
    return [int(best[2][0]), int(best[2][1])]