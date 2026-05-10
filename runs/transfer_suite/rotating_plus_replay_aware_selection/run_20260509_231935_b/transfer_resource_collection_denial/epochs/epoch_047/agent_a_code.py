def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    res = set((p[0], p[1]) for p in resources if p and len(p) >= 2)
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not res:
        return [0, 0]

    best = [0, 0]
    bestd = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        mind = 10**9
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            ddx = nx - rx
            if ddx < 0:
                ddx = -ddx
            ddy = ny - ry
            if ddy < 0:
                ddy = -ddy
            d = ddx if ddx > ddy else ddy
            if d < mind:
                mind = d
        if mind < bestd:
            bestd = mind
            best = [dx, dy]
        elif mind == bestd:
            if (dx, dy) == (0, 0) and best != [0, 0]:
                continue
            if dx > best[0] or (dx == best[0] and dy > best[1]):
                best = [dx, dy]

    return best