def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    border = set()
    for ox, oy in oppT:
        for nx, ny in neighbors8(ox, oy):
            if (nx, ny) not in obstacles:
                border.add((nx, ny))

    target_pool = [c for c in border if (c in unclaimed)]
    if not target_pool:
        target_pool = [c for c in border if (c in oppT) or (c in unclaimed)]
    if not target_pool:
        target_pool = [c for c in (unclaimed or []) if c not in obstacles]
    if not target_pool:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    tx, ty = min(target_pool, key=lambda c: (dist((sx, sy), c), c[0], c[1]))

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        v = 0
        if (x, y) in unclaimed:
            v += 3
        elif (x, y) in oppT:
            v += 2
        elif (x, y) in selfT:
            v += 0
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in oppT:
                v += 0.5
            if (nx, ny) in unclaimed:
                v += 0.2
        return v

    best = None
    best_score = -10**18
    best_step = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            s = -10**9
        else:
            s = cell_value(nx, ny)
            s += (dist((nx, ny), (tx, ty)) * -0.05)
            s += (-0.01 * max(abs(dx), abs(dy)))
        if s > best_score or (s == best_score and (dx, dy) < best_step):
            best_score = s
            best_step = (dx, dy)
            best = (nx, ny)

    if best is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]