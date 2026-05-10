def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for c in observation.get("obstacles", []) or []:
        obstacles.add((int(c[0]), int(c[1])))

    self_cells = set()
    for c in observation.get("self_territory", []) or []:
        self_cells.add((int(c[0]), int(c[1])))

    opp_cells = set()
    for c in observation.get("opponent_territory", []) or []:
        opp_cells.add((int(c[0]), int(c[1])))

    unclaimed = set()
    for c in observation.get("unclaimed_cells", []) or []:
        unclaimed.add((int(c[0]), int(c[1])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    targets = list(unclaimed) if unclaimed else []
    if targets:
        tx, ty = min(targets, key=lambda p: (abs(p[0] - cx) + abs(p[1] - cy), abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        tx, ty = (int(cx), int(cy))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        d = abs(nx - tx) + abs(ny - ty)
        s = -d
        if (nx, ny) in unclaimed:
            s += 6
        if (nx, ny) in opp_cells:
            s += 9
        if (nx, ny) in self_cells:
            s += 1
        # mild anti-collision: avoid stepping toward opponent if it doesn't help target
        s -= 0.05 * (abs(nx - ox) + abs(ny - oy))
        return s

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score(nx, ny)
        if sc > best[0]:
            best = (sc, dx, dy)
        elif sc == best[0]:
            # deterministic tie-break: prefer stay, then smaller dx, then smaller dy
            if (dx, dy) == (0, 0):
                best = (sc, dx, dy)
            elif best[1:] != (0, 0,):
                if (dx, dy) < (best[1], best[2]):
                    best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]