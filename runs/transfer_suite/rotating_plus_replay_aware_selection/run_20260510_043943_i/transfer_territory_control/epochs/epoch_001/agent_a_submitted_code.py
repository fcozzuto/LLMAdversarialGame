def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (ox, oy))

    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    resources = observation.get("resources", [])
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if res:
            dmin = min(manh(nx, ny, rx, ry) for rx, ry in res)
            val = -dmin
        else:
            val = man(nx, ny, ox, oy)  # flee if no visible resources
        if val > bestv or (val == bestv and (best is None or (dx, dy) < best)):
            bestv = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]