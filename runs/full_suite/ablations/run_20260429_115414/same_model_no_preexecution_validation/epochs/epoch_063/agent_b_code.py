def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_obst(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx or ddy:
                    if (x + ddx, y + ddy) in obstacles:
                        c += 1
        return c

    best = None
    bestv = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Contest-aware: prefer resources we can reach sooner and that limit opponent advantage.
        risk = 0.65 * do - 1.1 * ds
        obst_pen = 0.12 * adj_obst(rx, ry)
        val = risk + obst_pen
        if bestv is None or val < bestv:
            bestv = val
            best = (rx, ry)

    tx, ty = best
    ddx = tx - sx
    ddy = ty - sy
    step_dx = 0 if ddx == 0 else (1 if ddx > 0 else -1)
    step_dy = 0 if ddy == 0 else (1 if ddy > 0 else -1)

    # Try preferred move first; if blocked, fall back in deterministic order.
    candidates = []
    candidates.append((step_dx, step_dy))
    for dx in (0, 1, -1):
        for dy in (0, 1, -1):
            if (dx, dy) != (step_dx, step_dy):
                candidates.append((dx, dy))
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]