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

    def dist(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # deterministic "escape" / center pressure
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            s = dist(nx, ny, tx, ty)
            if best is None or s < best[0]:
                best = (s, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose target where we have a race advantage: (my_dist - opp_dist) minimized
    best_target = None
    for rx, ry in resources:
        md = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (md - od, md, rx, ry)
        if best_target is None or key < best_target[0]:
            best_target = (key, rx, ry)
    _, tx, ty = best_target

    # Move greedily toward target while (secondarily) increasing opponent distance
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = dist(nx, ny, tx, ty)
        oppd = dist(ox, oy, tx, ty)
        # score: primary reduce myd; secondary make it harder for opponent if tie on myd
        score = (myd, -oppd, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_move is None or score < best_move[0]:
            best_move = (score, dx, dy)
    return [best_move[1], best_move[2]] if best_move else [0, 0]