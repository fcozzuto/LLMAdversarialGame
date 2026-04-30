def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = moves

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    if resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # minimize distance to nearest resource; penalize proximity to obstacles; deterministic tie-break by move order
            d = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            score = (d, obst_adj_pen(nx, ny), dx, dy)
            if best is None or score < best[0]:
                best = (score, (dx, dy))
        if best is not None:
            return [best[1][0], best[1][1]]

    # Fallback: move toward opponent, still avoiding obstacles
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        score = (d, obst_adj_pen(nx, ny), dx, dy)
        if best is None or score < best[0]:
            best = (score, (dx, dy))
    if best is not None:
        return [best[1][0], best[1][1]]

    return [0, 0]