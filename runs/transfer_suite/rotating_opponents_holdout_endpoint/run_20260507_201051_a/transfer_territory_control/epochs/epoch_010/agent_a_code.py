def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    # Prefer a frontier target (adjacent to our territory); otherwise any promising cell.
    neigh = []
    for tx, ty in self_terr:
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = tx + dx, ty + dy
            if inb(nx, ny) and (nx, ny) not in self_terr and (nx, ny) not in obstacles:
                neigh.append((nx, ny))
    candidates = set(neigh)
    candidates |= unclaimed
    candidates |= opp_terr

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in opp_terr:
            # Flipping on entry: prioritize conquest, but don't suicide into corners that trap you.
            return 200000 - man(x, y, ox, oy)
        if (x, y) in self_terr:
            return 1000 - (abs((w - 1) / 2 - x) + abs((h - 1) / 2 - y))
        if (x, y) in unclaimed:
            edge = (x == 0 or x == w - 1 or y == 0 or y == h - 1)
            corner = ((x == 0 or x == w - 1) and (y == 0 or y == h - 1))
            return (1200 if edge else 400) + (800 if corner else 0) - man(x, y, ox, oy) * 2
        return 0

    if not candidates:
        return [0, 0]

    # Pick target maximizing (value - distance).
    best_t = None
    best_s = -10**18
    for x, y in candidates:
        sc = cell_value(x, y) - 3 * man(x, y, sx, sy)
        if sc > best_s:
            best_s = sc
            best_t = (x, y)
    tx, ty = best_t

    # Choose best immediate step toward target while improving cell value.
    best_move = (0, 0)
    best_msc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        progress = man(sx, sy, tx, ty) - man(nx, ny, tx, ty)
        msc = cell_value(nx, ny) + 5 * progress
        if msc > best_msc:
            best_msc = msc
            best_move = (dx, dy)

    # Deterministic fallback: if all were blocked, stay.
    return [int(best_move[0]), int(best_move[1])]