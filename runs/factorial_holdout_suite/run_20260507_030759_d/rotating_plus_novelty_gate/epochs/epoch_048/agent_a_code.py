def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)

    res_list = observation.get("resources", []) or []
    resources = set(tuple(r) for r in res_list)

    dxs = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))

    if not legal:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]
    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dself = abs(nx - ox) + abs(ny - oy)
            cand = (-dself, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dres = min(manh(nx, ny, rx, ry) for rx, ry in resources)
        dobj = manh(nx, ny, ox, oy)
        cand = (dres, -dobj, dx, dy)
        if best is None or cand < best:
            best = cand
    return [best[2], best[3]]