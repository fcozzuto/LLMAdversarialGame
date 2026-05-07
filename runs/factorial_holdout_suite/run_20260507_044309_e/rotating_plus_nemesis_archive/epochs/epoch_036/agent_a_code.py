def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for t in observation.get("obstacles") or []:
        try:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))
        except:
            pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            nr = min((man(nx, ny, rx, ry), rx, ry) for rx, ry in resources)
            dres = nr[0]
            val = dres * 1000 + man(nx, ny, ox, oy)
        else:
            val = man(nx, ny, ox, oy) * 10 - (abs(nx - sx) + abs(ny - sy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]