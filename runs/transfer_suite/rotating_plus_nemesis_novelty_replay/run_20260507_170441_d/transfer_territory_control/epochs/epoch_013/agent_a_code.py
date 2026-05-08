def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = observation.get("resources", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []
    targets = unclaimed if unclaimed else resources

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]

    if targets:
        best = None
        tx, ty = None, None
        for t in targets:
            try:
                x, y = int(t[0]), int(t[1])
            except:
                continue
            d = abs(x - sx) + abs(y - sy)
            if best is None or d < best or (d == best and (x, y) < (tx, ty)):
                best = d
                tx, ty = x, y
    else:
        tx, ty = ox, oy

    cur = (sx, sy)
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        score = -2 * (abs(tx - nx) + abs(ty - ny)) + (abs(nx - ox) + abs(ny - oy))
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]