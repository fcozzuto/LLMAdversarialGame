def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_move = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Greedy: closest resource; tie-break by farther from opponent
            dmin = None
            for rx, ry in resources:
                dd = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if dmin is None or dd < dmin:
                    dmin = dd
            vd = (dmin, -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)))
            if bestv is None or vd < bestv:
                bestv = vd
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: maximize distance from opponent deterministically
    best_move = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        vd = -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
        if bestv is None or vd < bestv:
            bestv = vd
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]