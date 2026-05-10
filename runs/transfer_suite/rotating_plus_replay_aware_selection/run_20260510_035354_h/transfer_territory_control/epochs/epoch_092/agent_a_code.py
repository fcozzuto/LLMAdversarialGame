def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", [0, 0])
    bx, by = observation.get("opponent_position", [0, 0])
    try:
        ax, ay = int(ax), int(ay)
        bx, by = int(bx), int(by)
    except:
        ax, ay, bx, by = 0, 0, 0, 0

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    uset = toset(observation.get("self_territory"))
    ucell = toset(observation.get("unclaimed_cells"))
    obset = toset(observation.get("obstacles"))
    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obset

    frontier = set()
    if uset:
        for x, y in uset:
            for dx, dy in neigh8:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in ucell:
                    frontier.add((nx, ny))

    dirs = neigh8
    best = None
    best_sc = -10**9

    targets = frontier if frontier else (ucell if ucell else {(bx, by)})
    tx, ty = bx, by

    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        sc = -abs(nx - tx) - abs(ny - ty)  # default: move toward opponent
        if (nx, ny) in ucell:
            sc += 5000
        if (nx, ny) in frontier:
            sc += 10000
        if uset and (nx, ny) in {(x + ddx, y + ddy) for (x, y) in uset for ddx, ddy in neigh8}:
            sc += 200  # mild boost for staying near our territory
        if targets and (nx, ny) in targets:
            sc += 1000
        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    return list(best if best is not None else (0, 0))