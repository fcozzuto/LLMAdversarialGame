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

    # Approximate "nearest unclaimed" distance for bias; limited samples for speed.
    ulist = list(unclaimed)
    def nearest_unclaimed_dist(nx, ny):
        if not ulist:
            return 99
        best = 999
        lim = 24
        for i in range(min(lim, len(ulist))):
            tx, ty = ulist[i]
            d = abs(nx - tx) + abs(ny - ty)
            if d < best:
                best = d
        return best

    best_score = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            if dx == 0 and dy == 0:
                score = -10**9
            else:
                continue
        else:
            adj_self = adj_count(nx, ny, self_ter)
            adj_opp = adj_count(nx, ny, opp_ter)
            adj_unc = adj_count(nx, ny, unclaimed)

            cell = (nx, ny)
            score = 0.0
            score += adj_self * 2.0
            score += adj_unc * 1.2
            score -= adj_opp * 3.0

            if cell in opp_ter:
                score += 12.0 - adj_opp * 1.5
            if cell in self_ter:
                score -= 0.4

            score += -0.15 * (abs(nx - ox) + abs(ny - oy))
            score += -0.05 * nearest_unclaimed_dist(nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move