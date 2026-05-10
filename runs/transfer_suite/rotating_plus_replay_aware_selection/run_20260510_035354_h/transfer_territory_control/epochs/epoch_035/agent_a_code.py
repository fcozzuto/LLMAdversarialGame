def choose_move(observation):
    ax, ay = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o
            if inb(x, y):
                blocked.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r
            if inb(x, y) and (x, y) not in blocked:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bd = 10**18
        for dx, dy in moves:
            nx, ny = ax + dx, ay + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if d < bd:
                bd = d
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    res_sorted = sorted(res)
    best = None
    bd = 10**18
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        if (nx, ny) in res:
            return [dx, dy]
        dmin = 10**18
        for tx, ty in res_sorted:
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if d < dmin:
                dmin = d
        if dmin < bd or (dmin == bd and (dx, dy) < best):
            bd = dmin
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]