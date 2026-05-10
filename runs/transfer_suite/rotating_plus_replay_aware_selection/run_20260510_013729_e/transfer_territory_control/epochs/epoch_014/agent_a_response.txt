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

    def neigh8_count(nx, ny, cellset):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in cellset:
                    c += 1
        return c

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            dx, dy = 0, 0
            nx, ny = x, y

        in_self = (nx, ny) in self_ter
        in_opp = (nx, ny) in opp_ter
        in_un = (nx, ny) in unclaimed

        adj_self = neigh8_count(nx, ny, self_ter)
        adj_opp = neigh8_count(nx, ny, opp_ter)

        dopp = abs(nx - ox) + abs(ny - oy)
        dist_pen = -0.08 * dopp

        base = 0
        if in_opp:
            base += 7
        elif in_un:
            base += 4
        elif in_self:
            base += 1

        attack_bias = 1.2 * adj_opp - 0.4 * adj_self
        frontier_bias = 0.9 * adj_self

        score = base + attack_bias + frontier_bias + dist_pen

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]