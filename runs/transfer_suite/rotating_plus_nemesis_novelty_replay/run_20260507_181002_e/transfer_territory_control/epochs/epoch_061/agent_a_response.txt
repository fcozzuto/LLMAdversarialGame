def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)
    if not unclaimed:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def adj8(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    # Prefer expansion from our territory border
    border = []
    if selfT:
        for (tx, ty) in unclaimed:
            for (ax, ay) in adj8(tx, ty):
                if (ax, ay) in selfT:
                    if (tx, ty) not in obstacles:
                        border.append((tx, ty))
                    break
    candidates = border or [c for c in unclaimed if c not in obstacles]
    if not candidates:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    bestv = -10**18
    for tx, ty in candidates:
        if (tx, ty) in obstacles:
            continue
        ds = abs(sx - tx) + abs(sy - ty)
        do = abs(ox - tx) + abs(oy - ty)
        dc = abs(tx - cx) + abs(ty - cy)
        # Win race when we are closer; otherwise still prefer contestable and central points
        v = (do - ds) * 4.0 - ds * 0.15 + dc * 0.02
        # Slight bias to cells closer to us than opponent
        if ds <= do:
            v += 0.5
        # Deterministic tie-break
        if v > bestv or (v == bestv and (tx, ty) < best):
            bestv = v
            best = (tx, ty)

    tx, ty = best
    # Move one step towards target; avoid stepping into obstacles if possible
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try best direction among neighbors (including staying) that reduces distance to target
    curd = abs(sx - tx) + abs(sy - ty)
    beststep = (0, 0)
    bestdist = curd + 1
    for mdx, mdy in dirs:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = abs(nx - tx) + abs(ny - ty)
        if nd < bestdist or (nd == bestdist and (mdx, mdy) < beststep):
            bestdist = nd
            beststep = (mdx, mdy)

    return [int(beststep[0]), int(beststep[1])]