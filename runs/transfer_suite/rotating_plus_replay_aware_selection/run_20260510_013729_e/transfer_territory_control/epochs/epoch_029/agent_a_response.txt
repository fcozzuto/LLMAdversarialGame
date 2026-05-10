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
    resources = set(map(tuple, observation.get("resources", [])))

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

    best_sc = -10**18
    best_mv = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_self = adj_count(nx, ny, self_ter)
        adj_opp = adj_count(nx, ny, opp_ter)
        dopp = abs(nx - ox) + abs(ny - oy)

        if (nx, ny) in resources:
            base = 20
        elif (nx, ny) in unclaimed:
            base = 8
        elif (nx, ny) in self_ter:
            base = 2
        elif (nx, ny) in opp_ter:
            base = 6
        else:
            base = 0

        on_edge = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        sc = (
            base
            + 2.5 * adj_self
            + 2.0 * on_edge
            - 2.0 * adj_opp
            + (0.9 if (nx, ny) in opp_ter else 0.0)  # favor flipping entry into opponent cells
            - 0.08 * dopp  # don't drift too far from center of contest
        )

        if sc > best_sc:
            best_sc = sc
            best_mv = [dx, dy]

    return [int(best_mv[0]), int(best_mv[1])]