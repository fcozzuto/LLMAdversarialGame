def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    if not unclaimed:
        unclaimed = set(resources)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def count_adj(s, x, y):
        c = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in s:
                c += 1
        return c

    best = (float("-inf"), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        u = 0.0
        if (nx, ny) in selfT:
            u += 0.2
        if (nx, ny) in unclaimed:
            u += 1.8 + 0.05 * count_adj(unclaimed, nx, ny)
        if (nx, ny) in oppT:
            u += 4.0 + 0.2 * count_adj(oppT, nx, ny)
        if (nx, ny) not in selfT:
            u += 0.2 * count_adj(selfT, nx, ny)
        u += 0.15 * count_adj(oppT, nx, ny)  # pressure to counterclaim
        u -= 0.01 * (abs(nx - cx) + abs(ny - cy))
        if u > best[0] + 1e-12:
            best = (u, dx, dy)

    if best[1] == 0 and best[2] == 0:
        # if all moves blocked, stay still
        return [0, 0]
    return [best[1], best[2]]