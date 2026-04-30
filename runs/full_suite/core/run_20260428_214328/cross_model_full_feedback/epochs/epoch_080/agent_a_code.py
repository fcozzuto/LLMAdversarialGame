def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target = None
    best = None
    for r in resources:
        myd = cheb((sx, sy), r)
        opd = cheb((ox, oy), r)
        # Prefer resources where we have a distance advantage; also prefer closer resources overall.
        score = (opd - myd) * 10 - myd
        if best is None or score > best or (score == best and r < target):
            best = score
            target = r

    if target is not None:
        tx, ty = target
        desired = (0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1))
        cand = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                d = cheb((nx, ny), target)
                cand.append((0 if (dx, dy) == desired else 1, d, dx, dy))
        cand.sort()
        return [int(cand[0][2]), int(cand[0][3])]

    # No resources: move to a "pivot" that generally contests the board, while keeping away from obstacles.
    pivot = (3, 3) if (sx + sy) <= (ox + oy) else (4, 4)
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            d = cheb((nx, ny), pivot)
            # small preference to not head straight toward opponent
            pen = cheb((nx, ny), (ox, oy))
            cand.append((d, -pen, dx, dy))
    cand.sort()
    return [int(cand[0][2]), int(cand[0][3])]