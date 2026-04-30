def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx, dy = min(legal, key=lambda d: cheb(sx + d[0], sy + d[1], tx, ty))
        return [dx, dy]

    best = None
    bestv = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        mind = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        tie = mind == opp
        v = (mind, 0 if tie else 1)  # prefer strictly better than opponent when close
        if best is None or v < bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]