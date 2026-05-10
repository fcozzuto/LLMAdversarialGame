def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    unclaimed = observation.get("unclaimed_cells", []) or []
    targets = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obst:
                targets.append((x, y))

    # Choose deterministic target: nearest unclaimed to opponent if any, else nearest to self.
    if targets:
        best = None
        bestv = None
        for (x, y) in targets:
            v = man(x, y, ox, oy) * 1000 + man(x, y, sx, sy)
            if bestv is None or v < bestv or (v == bestv and (x, y) < best):
                bestv = v
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = ox, oy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    bestm = None
    bests = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # Prefer moving closer to target; slight bias toward opponent.
        dist = man(nx, ny, tx, ty)
        opp = man(nx, ny, ox, oy)
        sc = dist * 10 + opp
        if bests is None or sc < bests or (sc == bests and (dx, dy) < bestm):
            bests = sc
            bestm = [dx, dy]

    if bestm is None:
        # If fully blocked, stay.
        return [0, 0]
    return bestm