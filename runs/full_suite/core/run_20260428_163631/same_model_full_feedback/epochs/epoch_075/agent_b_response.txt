def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w - 1 if sx < w // 2 else 0, h - 1 if sy < h // 2 else 0
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    my_near = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
    op_near = min(resources, key=lambda r: cheb(ox, oy, r[0], r[1]))

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_my = cheb(nx, ny, my_near[0], my_near[1])
        d_op = cheb(nx, ny, op_near[0], op_near[1])
        d_opcur = cheb(ox, oy, op_near[0], op_near[1])
        # Attack/deny: get closer to our nearest; simultaneously try to increase distance from where opponent likely goes.
        v = -(d_my * 10 + cheb(nx, ny, op_near[0], op_near[1]) * 2)
        # If we can "outreach" the opponent's target next step, prioritize it deterministically.
        v += 6 if cheb(nx, ny, op_near[0], op_near[1]) > d_opcur else 0
        # Micro-tie-breaker: prefer moves that reduce distance to the opponent position (control the race).
        v += -cheb(nx, ny, ox, oy) * 0.1
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]