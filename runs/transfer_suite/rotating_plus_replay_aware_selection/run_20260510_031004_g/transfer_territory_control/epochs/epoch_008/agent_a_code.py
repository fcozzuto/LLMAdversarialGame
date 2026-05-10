def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    resources = set(map(tuple, observation.get("resources", [])))

    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def neighbors(x, y):
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                yield nx, ny

    best = None
    best_move = [0, 0]

    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if (nx, ny) in opp_terr:
            gain = 2.5
        elif (nx, ny) in unclaimed:
            gain = 1.5
        elif (nx, ny) in resources:
            gain = 1.0
        elif (nx, ny) in self_terr:
            gain = 0.2
        else:
            gain = 0.3

        adj_uncl = 0
        adj_opp = 0
        for ax, ay in neighbors(nx, ny):
            if (ax, ay) in unclaimed:
                adj_uncl += 1
            if (ax, ay) in opp_terr:
                adj_opp += 1

        dist_center = abs(nx - cx) + abs(ny - cy)
        score = gain + 0.25 * adj_uncl - 0.12 * adj_opp - 0.01 * dist_center

        key = (score, adj_uncl, -adj_opp, -abs(dx) - abs(dy), -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return best_move