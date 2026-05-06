def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        bd = 10**9
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if d < bd:
                bd = d
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        if (tx, ty) in obstacles:
            tx, ty = sx, sy

    if tx == sx and ty == sy:
        return [0, 0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
        if dx != 0:
            nx2, ny2 = sx + dx, sy
            if 0 <= nx2 < w and (nx2, ny2) not in obstacles:
                return [dx, 0]
        if dy != 0:
            nx2, ny2 = sx, sy + dy
            if 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                return [0, dy]
        for mx, my in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nx2, ny2 = sx + mx, sy + my
            if 0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                return [mx, my]
        return [0, 0]

    return [dx, dy]