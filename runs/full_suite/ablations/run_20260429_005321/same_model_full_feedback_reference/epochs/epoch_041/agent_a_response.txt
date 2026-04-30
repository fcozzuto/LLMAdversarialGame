def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        target = (int((w - 1) / 2), int((h - 1) / 2))
    else:
        best = None
        best_score = -10**18
        for (x, y) in resources:
            myd = cheb(sx, sy, x, y)
            opd = cheb(ox, oy, x, y)
            adv = opd - myd
            center_pen = int(abs(x - cx) + abs(y - cy))
            score = (adv * 1000) - (myd * 10) - (opd * 2) - center_pen
            if score > best_score or (score == best_score and (x, y) < best):
                best_score = score
                best = (x, y)
        target = best

    best_move = (0, 0)
    best_mscore = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd2 = cheb(nx, ny, target[0], target[1])
        opd2 = cheb(ox, oy, target[0], target[1])
        center_bias = -(abs(nx - cx) + abs(ny - cy))
        mscore = (-myd2 * 1000) + (opd2 * 50) + center_bias
        if mscore > best_mscore or (mscore == best_mscore and (dx, dy) < best_move):
            best_mscore = mscore
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]