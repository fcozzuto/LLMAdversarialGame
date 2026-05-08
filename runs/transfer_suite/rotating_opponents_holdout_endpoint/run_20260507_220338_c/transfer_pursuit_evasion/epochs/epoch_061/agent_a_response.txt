def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("avoid" in role_s) or ("runner" in role_s) or ("flee" in role_s) or ("evade" in role_s)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y, tx, ty):
        dx = abs(tx - x)
        dy = abs(ty - y)
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                m += 1
        return m

    def obstacle_adjacency(x, y):
        a = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in blocked:
                a += 1
        return a

    best = None
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        dist = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        adj = obstacle_adjacency(nx, ny)
        if is_evader:
            v = (dist * 100) + (mob * 2) - (adj * 5)
            # Add slight preference to move away in dominant axis to break cornering
            v += (abs(nx - ox) + abs(ny - oy))
        else:
            v = (-dist * 100) + (mob * 2) - (adj * 5)
        if bestv is None or v > bestv or (v == bestv and (dx, dy) == (0, 0)):
            bestv = v
            best = (dx, dy)

    if best is None:
        # Fallback: stay put
        return [0, 0]
    return [int(best[0]), int(best[1])]