def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        for nx, ny in ((0, 0), (1, 0), (0, 1), (1, 1), (sx, sy), (sx + 1, sy), (sx - 1, sy), (sx, sy + 1), (sx, sy - 1)):
            nx, ny = int(nx), int(ny)
            if ok(nx, ny):
                sx, sy = nx, ny
                break
        else:
            return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    best = None
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        if best is None or d < best_d or (d == best_d and (dx, dy) < best):
            best = (dx, dy)
            best_d = d

    if best is None:
        return [0, 0]
    return [best[0], best[1]]