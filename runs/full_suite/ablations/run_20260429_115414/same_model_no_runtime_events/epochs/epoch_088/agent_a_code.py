def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        dx = 0 if ox == sx else (1 if ox < sx else -1)
        dy = 0 if oy == sy else (1 if oy < sy else -1)
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if inb(nx, ny):
                if mx == dx and my == dy:
                    return [mx, my]
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if inb(nx, ny):
                return [mx, my]
        return [0, 0]

    best = None
    best_score = -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        rdist = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        odist = cheb(nx, ny, ox, oy)
        score = -rdist * 10 - odist * 2
        if odist == 0:
            score -= 100000
        elif odist == 1:
            score -= 200
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                    c += 1
        score -= c
        if best is None or score > best_score:
            best_score = score
            best = (mx, my)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]