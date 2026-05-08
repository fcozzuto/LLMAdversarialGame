def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    unclaimed = observation.get("unclaimed_cells", []) or []
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if unclaimed:
        best = None
        bestv = None
        for x, y in unclaimed:
            if not inb(x, y) or (x, y) in obstacles:
                continue
            ds = man(sx, sy, x, y)
            do = man(ox, oy, x, y)
            v = ds - do * 0.7  # prefer cells we can reach earlier
            if bestv is None or v < bestv:
                bestv = v
                best = (x, y)
        if best is None:
            best = None

    tx, ty = (best if unclaimed and best is not None else (ox, oy))
    if not unclaimed or best is None:
        # If no target, move toward opponent slightly
        tx, ty = ox, oy

    cand = []
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        score = -ds + 0.2 * do
        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort()
    _, dx, dy = cand[-1]
    return [int(dx), int(dy)]