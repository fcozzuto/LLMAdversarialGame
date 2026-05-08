def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    self_t = set()
    for c in observation.get("self_territory") or []:
        if c is not None and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                self_t.add((x, y))

    unclaimed = []
    for c in observation.get("unclaimed_cells") or []:
        if c is not None and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    target = None
    frontier = []
    if self_t:
        for (x, y) in self_t:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    frontier.append((nx, ny))
        frontier = list({p for p in frontier if p in set(unclaimed)})

    if frontier:
        # choose nearest frontier cell to self
        bestd = None
        for (tx, ty) in frontier:
            d = abs(tx - sx) + abs(ty - sy)
            if bestd is None or d < bestd or (d == bestd and (tx, ty) < target):
                bestd = d
                target = (tx, ty)
    elif unclaimed:
        bestd = None
        target = unclaimed[0]
        for (tx, ty) in unclaimed:
            d = abs(tx - sx) + abs(ty - sy)
            if bestd is None or d < bestd or (d == bestd and (tx, ty) < target):
                bestd = d
                target = (tx, ty)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            if target is None:
                score = 0
            else:
                score = -(abs(nx - target[0]) + abs(ny - target[1]))
            # tie-break: stay farther from opponent
            score = (score, (abs(nx - ox) + abs(ny - oy)), -abs(dx) - abs(dy))
            candidates.append(((dx, dy), score))

    candidates.sort(key=lambda t: (t[1][0], t[1][1], t[1][2]), reverse=True)
    return list(candidates[0][0]) if candidates else [0, 0]