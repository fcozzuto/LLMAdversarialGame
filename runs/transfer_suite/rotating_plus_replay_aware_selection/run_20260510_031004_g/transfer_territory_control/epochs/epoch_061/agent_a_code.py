def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if dx == 0 and dy == 0:
            if not free(nx, ny):
                nx, ny = sx, sy
            dist = abs(sx - ox) + abs(sy - oy)
        else:
            if not free(nx, ny):
                continue
            dist = abs(nx - ox) + abs(ny - oy)
        cand = (dist, abs(dx) + abs(dy), dx, dy, nx, ny)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[2], best[3]]