def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    resources = observation.get("resources", None)
    rlist = []
    if resources is None:
        rlist = []
    elif isinstance(resources, dict):
        for k, v in resources.items():
            if isinstance(k, (list, tuple)) and len(k) >= 2:
                rlist.append((int(k[0]), int(k[1])))
            elif isinstance(v, (list, tuple)) and len(v) >= 2:
                rlist.append((int(v[0]), int(v[1])))
    else:
        try:
            for r in resources:
                if isinstance(r, (list, tuple)) and len(r) >= 2:
                    rlist.append((int(r[0]), int(r[1])))
        except TypeError:
            rlist = []

    opp_close = man(sx, sy, ox, oy) <= 2
    target = None
    bestd = None
    for rx, ry in rlist:
        if 0 <= rx < w and 0 <= ry < h and free(rx, ry):
            d = man(sx, sy, rx, ry)
            if bestd is None or d < bestd:
                bestd, target = d, (rx, ry)

    best_score = None
    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if target is not None:
            score = -man(nx, ny, target[0], target[1])
            score += 0.25 * man(nx, ny, ox, oy)  # keep some distance
            if opp_close:
                score += 0.75 * man(nx, ny, ox, oy)
        else:
            score = man(nx, ny, ox, oy)  # maximize distance when no resources

        key = (score, -dx, -dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]