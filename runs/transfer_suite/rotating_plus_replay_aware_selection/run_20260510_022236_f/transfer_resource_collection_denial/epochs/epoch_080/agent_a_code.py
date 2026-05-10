def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        try:
            x, y = o
        except Exception:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = r
        except Exception:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not inb(sx, sy) or (sx, sy) in obs:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    if not res:
        best = (10**12, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    best = (10**12, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        mind = 10**12
        for rx, ry in res:
            dist = abs(nx - rx) + abs(ny - ry)
            if dist < mind:
                mind = dist
        if mind < best[0] or (mind == best[0] and (dx, dy) < (best[1], best[2])):
            best = (mind, dx, dy)
    return [best[1], best[2]]