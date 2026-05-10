def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = set(map(tuple, observation.get("resources", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            score = 10_000 - (abs(nx - px) + abs(ny - py))
        else:
            score = 0
            if (nx, ny) in unclaimed:
                score += 200
            if (nx, ny) in resources:
                score += 80
            if (nx, ny) in self_terr:
                score -= 5
            score += - (abs(nx - px) + abs(ny - py))
        key = (score, -dx, -dy, nx, ny)
        if best is None or key > best[0]:
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]