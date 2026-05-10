def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (ox, oy))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", [])))
    resources = list(map(tuple, observation.get("resources", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    target = None
    bestd = None
    for cells in (unclaimed, resources):
        for x, y in cells:
            if (x, y) in obstacles:
                continue
            d = abs(x - ox) + abs(y - oy)
            if bestd is None or d < bestd or (d == bestd and (x, y) < target):
                bestd = d
                target = (x, y)
        if target is not None:
            break
    if target is None:
        target = (px, py)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(target[0] - nx) + abs(target[1] - ny)
        score = (-d, nx, ny)
        if best is None or score > best:
            best = score
            bestmove = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(bestmove[0]), int(bestmove[1])]