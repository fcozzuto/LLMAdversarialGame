def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            valid.append((dx, dy))

    if not valid:
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y):
                resources.append((x, y))

    unclaimed = []
    for c in observation.get("unclaimed_cells") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if inside(x, y):
                unclaimed.append((x, y))

    if resources:
        tx, ty = min(resources, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    elif unclaimed:
        tx, ty = min(unclaimed, key=lambda t: (abs(t[0] - ox) + abs(t[1] - oy), t[0], t[1]))
    else:
        tx, ty = ox, oy

    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        dist = abs(nx - tx) + abs(ny - ty)
        score = (dist, abs(nx - ox) + abs(ny - oy), -((nx + ny) & 1), dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]