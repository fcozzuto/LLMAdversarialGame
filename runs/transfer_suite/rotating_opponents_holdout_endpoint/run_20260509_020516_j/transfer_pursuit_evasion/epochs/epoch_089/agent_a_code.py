def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    res = []
    for it in observation.get("resources") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if res:
            dmin = 10**9
            hit = 0
            for rx, ry in res:
                if rx == nx and ry == ny:
                    hit = 1
                    break
                d = abs(rx - nx) + abs(ry - ny)
                if d < dmin:
                    dmin = d
            dres = 0 if hit else dmin
        else:
            dres = 10**6
            hit = 0
        dop = abs(ox - nx) + abs(oy - ny)
        val = (hit, dres, dop, -abs(dx) - abs(dy))
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best