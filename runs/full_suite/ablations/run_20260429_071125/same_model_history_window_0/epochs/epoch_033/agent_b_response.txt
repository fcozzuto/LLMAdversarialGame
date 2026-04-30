def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)
    occ.add((ox, oy))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        best = [0, 0]
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            v = dist((nx, ny), (cx, cy)) - 0.15 * dist((nx, ny), (ox, oy))
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Evaluate moves by closeness to nearest resource, with mild safety vs opponent.
    best = [0, 0]
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        nr = min(resources, key=lambda r: dist((nx, ny), (r[0], r[1])))
        v = dist((nx, ny), (nr[0], nr[1]))
        v += 0.03 * dist((nx, ny), (cx, cy))
        v -= 0.08 * dist((nx, ny), (ox, oy))
        if bestv is None or v < bestv:
            bestv = v
            best = [dx, dy]
    return best