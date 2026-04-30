def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    try:
        sx, sy = int(sp[0]), int(sp[1])
    except:
        sx, sy = 0, 0
    try:
        ox, oy = int(op[0]), int(op[1])
    except:
        ox, oy = w - 1, h - 1

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    if resources:
        tx, ty = min(resources, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        tx, ty = ox, oy

    curd = abs(tx - sx) + abs(ty - sy)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = abs(tx - nx) + abs(ty - ny)
        if d < curd or best is None:
            best = (dx, dy, d)
        elif d == best[2]:
            if (dx, dy) < (best[0], best[1]):
                best = (dx, dy, d)

    if best is not None:
        return [best[0], best[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]