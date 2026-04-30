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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        for rx, ry in resources:
            dso = dist(sx, sy, rx, ry)
            dpo = dist(ox, oy, rx, ry)
            tie = 0 if best is None else best[0]
            val = (dso - dpo, dso)
            if best is None or val < tie:
                best = (val, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (10**9, 0, 0, sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to = dist(nx, ny, tx, ty)
        d_opp = dist(nx, ny, ox, oy)
        on_res = 1 if (nx, ny) in resources else 0
        score = (-2 * on_res) + d_to - 0.25 * d_opp
        if score < best_move[0]:
            best_move = (score, dx, dy, nx, ny)

    _, dx, dy, _, _ = best_move
    return [int(dx), int(dy)]