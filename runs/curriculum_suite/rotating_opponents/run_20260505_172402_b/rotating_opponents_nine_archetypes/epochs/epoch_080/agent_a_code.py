def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        for y in range(h):
            for x in range(w):
                if inb(x, y):
                    sx, sy = x, y
                    break
            else:
                continue
            break

    target = None
    if resources:
        bestd = None
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if bestd is None or d < bestd or (d == bestd and (x, y) < target):
                bestd = d
                target = (x, y)
    else:
        target = (w // 2, h // 2)

    best = None
    # deterministic tie-breaking by move order
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_to_target = cheb(nx, ny, target[0], target[1])
            d_to_opp = cheb(nx, ny, ox, oy)
            score = (0 if resources else 1, -d_to_opp, -d_to_target, dx, dy)
            if best is None or score > best[0]:
                best = (score, [dx, dy])

    if best is None:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    return [dx, dy]
        return [0, 0]

    return best[1]