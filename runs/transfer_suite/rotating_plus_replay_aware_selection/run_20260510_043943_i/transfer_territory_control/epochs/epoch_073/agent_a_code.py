def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                unclaimed.append((x, y))

    def d2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    tx = ty = None
    best = None
    if resources:
        for x, y in resources:
            dd = d2(sx, sy, x, y)
            if best is None or dd < best or (dd == best and (x < tx or y < ty)):
                best = dd
                tx, ty = x, y
    elif unclaimed:
        for x, y in unclaimed:
            dd = d2(sx, sy, x, y)
            if best is None or dd < best or (dd == best and (x < tx or y < ty)):
                best = dd
                tx, ty = x, y
    else:
        op = observation.get("opponent_position") or (sx, sy)
        ox, oy = int(op[0]), int(op[1])
        tx, ty = ox, oy

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = -d2(nx, ny, tx, ty)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    return [dx, dy]