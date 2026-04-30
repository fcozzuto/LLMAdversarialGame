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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    try:
        rem = int(observation.get("remaining_resource_count") or 0)
    except:
        rem = 0
    late = rem <= 4

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = 0 if sx < w // 2 else w - 1, 0 if sy < h // 2 else h - 1
    else:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier than opponent; late-game prefer shortest distance.
            score = (myd - opd * (0.8 if not late else 0.6)) * 2 + myd * (0.6 if late else 0.3)
            # Small deterministic tie-breaker: closer to our current direction toward target.
            tie = abs((rx - sx)) + abs((ry - sy))
            cand = (score, tie, rx, ry)
            if best is None or cand < best:
                best = cand
        _, _, tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_val = (curd, 1 if (sx == tx and sy == ty) else 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Mildly avoid moving toward opponent late-game if equally good for resource.
        oppd = cheb(nx, ny, ox, oy)
        val = (nd, 0 if not late else nd - oppd * 0.05, abs(dx) + abs(dy))
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]