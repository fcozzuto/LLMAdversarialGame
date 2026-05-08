def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in v or []:
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    adj8 = dirs[:-1]  # exclude stay

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    best = [0, 0]
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        cell_sc = 0
        if (nx, ny) in oppT:
            cell_sc += 6  # flipping on entry
        elif (nx, ny) in unclaimed:
            cell_sc += 3
        elif (nx, ny) in selfT:
            cell_sc += 0
        else:
            cell_sc += 1  # empty/other territory

        # Frontier pressure: prefer cells that touch unclaimed or opponent territory
        frontier = 0
        for ax, ay in adj8:
            tx, ty = nx + ax, ny + ay
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            if (tx, ty) in oppT:
                frontier += 2
            elif (tx, ty) in unclaimed:
                frontier += 1

        # Avoid getting too close to opponent if not flipping target
        dist = abs(nx - ox) + abs(ny - oy)
        avoid = 0
        if (nx, ny) not in oppT:
            if dist <= 2:
                avoid = -2
            elif dist <= 1:
                avoid = -4

        # Slight tie-break toward reducing distance to opponent to enable flips
        prox = -0.05 * dist

        sc = cell_sc + 0.9 * frontier + avoid + prox
        if sc > best_sc:
            best_sc = sc
            best = [dx if (sx + dx == nx and sy + dy == ny) else 0, dy if (sx + dx == nx and sy + dy == ny) else 0]
            # If we forced to stay due to obstacle/out of bounds, keep dx/dy=0.
            if (nx, ny) == (sx, sy) and (dx, dy) != (0, 0):
                best = [0, 0]

    return [int(best[0]), int(best[1])]