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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    legal = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    if resources:
        best = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            score = (od - sd) * 10 - sd  # prioritize stealing/controlling targets
            if best is None or score > best[0]:
                best = (score, tx, ty, sd)
        _, tx, ty, _ = best

        step_dx = 0 if tx == sx else (1 if tx > sx else -1)
        step_dy = 0 if ty == sy else (1 if ty > sy else -1)

        candidates = []
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            nd = cheb(nx, ny, tx, ty)
            nod = cheb(nx, ny, ox, oy)
            od = cheb(ox, oy, tx, ty)
            steal = (od - nd)
            candidates.append((steal * 10 - nd - nod * 0.1, dx, dy))
        candidates.sort(reverse=True)
        return [int(candidates[0][1]), int(candidates[0][2])]

    # No visible resources: head toward center while moving away from opponent slightly
    cx, cy = w // 2, h // 2
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        nd = cheb(nx, ny, cx, cy)
        od = cheb(nx, ny, ox, oy)
        score = -nd + od * 0.05
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]