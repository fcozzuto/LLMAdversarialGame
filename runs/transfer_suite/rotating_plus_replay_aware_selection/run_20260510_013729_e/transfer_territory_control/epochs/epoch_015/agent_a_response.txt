def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_count(nx, ny, cellset):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in cellset:
                    c += 1
        return c

    def cell_score(nx, ny):
        aS = adj_count(nx, ny, self_ter)
        aO = adj_count(nx, ny, opp_ter)
        if (nx, ny) in self_ter:
            return 1 + aS - aO
        if (nx, ny) in unclaimed:
            return 4 + 3 * aS - 2 * aO - 0.05 * (abs(nx - ox) + abs(ny - oy))
        if (nx, ny) in opp_ter:
            # flipping helps only when we can strengthen our local perimeter
            return 6 + 4 * aS - 4 * aO - 0.02 * (abs(nx - ox) + abs(ny - oy))
        # occupied by neither (shouldn't happen often), discourage
        return -3 + aS - aO

    best_move = [0, 0]
    best_val = None
    tie_key = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = cell_score(nx, ny)
        tk = (-v, abs(nx - ox) + abs(ny - oy), dx, dy)  # deterministic tie-breaker
        if best_val is None or v > best_val or tk < tie_key:
            best_val = v
            tie_key = tk
            best_move = [dx, dy]

    return best_move