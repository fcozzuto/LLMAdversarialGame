def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        tx, ty = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))  # deterministic
    else:
        tx, ty = w // 2, h // 2

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    prefs = []
    prefs.append((dx, dy))
    prefs.append((dx, 0))
    prefs.append((0, dy))
    prefs.append((0, 0))
    # fallback: scan 8 moves in fixed order, avoid obstacles first
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            if (ddx, ddy) == (dx, dy) or (ddx == dx and ddy == 0) or (ddx == 0 and ddy == dy) or (ddx, ddy) == (0, 0):
                continue
            prefs.append((ddx, ddy))

    # optionally avoid opponent if extremely close
    if cheb(sx, sy, ox, oy) <= 1:
        prefs = [m for m in prefs if cheb(sx + m[0], sy + m[1], ox, oy) >= cheb(sx, sy, ox, oy)] + prefs

    for mdx, mdy in prefs:
        nx, ny = sx + mdx, sy + mdy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mdx), int(mdy)]

    return [0, 0]