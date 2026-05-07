def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = (10**9, 10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = (man(nx, ny, cx, cy), man(nx, ny, ox, oy))
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Choose target resource that maximizes our advantage: closer for us, farther for opponent.
    best_res = None
    best_res_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (sd, -od)  # primary: our closeness; tie: opponent farther
        if best_res_key is None or key < best_res_key:
            best_res_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    # Choose move that minimizes our distance to target; slight preference to increase opponent distance.
    best = (0, 0)
    bestv = (10**9, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)  # opponent pos unchanged this turn
        v = (sd, -od)
        if v < bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]