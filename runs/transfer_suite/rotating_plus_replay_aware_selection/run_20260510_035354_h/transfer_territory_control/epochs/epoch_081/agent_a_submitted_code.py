def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", [0, 0])
    ax, ay = int(ax), int(ay)
    opx, opy = observation.get("opponent_position", [0, 0])
    opx, opy = int(opx), int(opy)

    def toset(obj):
        s = set()
        if not obj:
            return s
        for p in obj:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    uset = toset(observation.get("self_territory"))
    oset = toset(observation.get("opponent_territory"))
    ucell = toset(observation.get("unclaimed_cells"))
    obset = toset(observation.get("obstacles"))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue
        v = 0
        if (nx, ny) in ucell:
            v += 200000
        if (nx, ny) in uset:
            v += 20000
        if (nx, ny) in oset:
            v -= 400000
        if nx == opx and ny == opy:
            v -= 800000

        mind = abs(nx - opx) + abs(ny - opy)
        v += 4000 - 5 * mind

        adj_o = 0
        adj_u = 0
        adj_us = 0
        for ddx, ddy in dirs:
            if ddx == 0 and ddy == 0:
                continue
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty):
                if (tx, ty) in oset:
                    adj_o += 1
                if (tx, ty) in ucell:
                    adj_u += 1
                if (tx, ty) in uset:
                    adj_us += 1
        v += 8000 * adj_o + 700 * adj_u + 500 * adj_us

        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]