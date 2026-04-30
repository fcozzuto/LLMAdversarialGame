def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target(tx, ty):
        tdx = sx - tx
        tdy = sy - ty
        return tdx if tdx >= 0 else -tdx, tdy if tdy >= 0 else -tdy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best = None
        bestd = None
        for x, y in resources:
            dx = sx - x
            if dx < 0:
                dx = -dx
            dy = sy - y
            if dy < 0:
                dy = -dy
            d = dx if dx > dy else dy
            if bestd is None or d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = ox, oy

    dx0, dy0 = tx - sx, ty - sy
    stepx = 0
    if dx0 > 0:
        stepx = 1
    elif dx0 < 0:
        stepx = -1
    stepy = 0
    if dy0 > 0:
        stepy = 1
    elif dy0 < 0:
        stepy = -1

    candidates = [(stepx, stepy), (stepx, 0), (0, stepy), (0, 0)]
    used = set()
    for m in candidates:
        if m not in used:
            used.add(m)
            nx, ny = sx + m[0], sy + m[1]
            if valid(nx, ny):
                return [m[0], m[1]]

    bestm = None
    bestscore = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        ddx = nx - tx
        if ddx < 0:
            ddx = -ddx
        ddy = ny - ty
        if ddy < 0:
            ddy = -ddy
        d = ddx if ddx > ddy else ddy
        score = d
        if bestscore is None or score < bestscore or (score == bestscore and (mx, my) < bestm):
            bestscore = score
            bestm = (mx, my)
    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]