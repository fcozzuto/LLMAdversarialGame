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

    def count_adj(nx, ny, cellset):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in cellset:
                    c += 1
        return c

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in self_ter:
            base = 0.4
        elif (nx, ny) in opp_ter:
            base = 1.6
        elif (nx, ny) in unclaimed:
            base = 2.2
        else:
            base = 0.8

        adj_unclaimed = count_adj(nx, ny, unclaimed)
        adj_self = count_adj(nx, ny, self_ter)
        adj_opp = count_adj(nx, ny, opp_ter)

        # Prefer expanding our frontier; mildly avoid stepping into opponent adjacency.
        frontier = 2.0 * adj_unclaimed + 0.4 * adj_self - 1.1 * adj_opp

        # Deterministic pressure: move toward the opponent while not breaking frontier control.
        dist_now = abs(x - ox) + abs(y - oy)
        dist_new = abs(nx - ox) + abs(ny - oy)
        approach = 0.35 * (dist_now - dist_new)

        # Encourage diagonal advance to compete with edge-claims.
        diag = 0.12 * (abs(nx - (w - 1 - ox)) + abs(ny - (h - 1 - oy)) - abs(x - (w - 1 - ox)) - abs(y - (h - 1 - oy)))

        score = base + frontier + approach + diag

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move