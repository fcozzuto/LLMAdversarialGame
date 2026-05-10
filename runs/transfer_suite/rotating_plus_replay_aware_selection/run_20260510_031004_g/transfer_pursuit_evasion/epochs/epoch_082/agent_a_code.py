def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    res = observation.get("resources", None)
    target = None
    bestd = None
    if isinstance(res, list) and res:
        for r in res:
            try:
                rx, ry = int(r[0]), int(r[1])
            except Exception:
                continue
            if (rx, ry) in obstacles or not inb(rx, ry):
                continue
            d = abs(rx - sx) + abs(ry - sy)
            if bestd is None or d < bestd:
                bestd = d
                target = (rx, ry)

    if target is None:
        target = (ox, oy)

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(target[0] - nx) + abs(target[1] - ny)
        opp_d = abs(target[0] - (ox)) + abs(target[1] - (oy))
        key = (d, abs(ox - nx) + abs(oy - ny), dx, dy, opp_d)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]