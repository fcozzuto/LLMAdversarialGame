def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = observation.get("obstacles", []) or []
    blocked = set()
    for p in obs:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                blocked.add((x, y))
        except:
            pass

    targets = (observation.get("unclaimed_cells") or None)
    if not targets:
        targets = observation.get("resources") or []
    tlist = []
    for p in targets:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in blocked:
                tlist.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (None, -10**18)

    def score(nx, ny):
        if (nx, ny) in blocked:
            return -10**18
        tx, ty = (nx, ny)
        if tlist:
            d2 = 10**18
            for (x, y) in tlist:
                dd = (x - nx) * (x - nx) + (y - ny) * (y - ny)
                if dd < d2:
                    d2, tx, ty = dd, x, y
            dist2 = d2
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            dist2 = (cx - nx) * (cx - nx) + (cy - ny) * (cy - ny)
        oppd = abs(ox - nx) + abs(oy - ny)
        avoid = 0
        if oppd <= 1:
            avoid = 50
        elif oppd == 2:
            avoid = 10
        return -dist2 - avoid * 1 + (2 if (nx, ny) == (ox, oy) else 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        sc = score(nx, ny)
        if sc > best[1]:
            best = ([dx, dy], sc)

    if best[0] is not None:
        return best[0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            return [dx, dy]
    return [0, 0]