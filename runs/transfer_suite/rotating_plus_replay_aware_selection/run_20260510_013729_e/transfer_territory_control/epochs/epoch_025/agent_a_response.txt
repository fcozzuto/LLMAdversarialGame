def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    if w <= 0 or h <= 0:
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
    def adj_count(nx, ny, s):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in s:
                    c += 1
        return c

    def man(nx, ny, a, b):
        return abs(nx - a) + abs(ny - b)

    near_opp = man(x, y, ox, oy) <= 3
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_self = adj_count(nx, ny, self_ter)
        adj_opp = adj_count(nx, ny, opp_ter)
        adj_un = adj_count(nx, ny, unclaimed)

        in_opp = (nx, ny) in opp_ter
        in_self = (nx, ny) in self_ter
        in_un = (nx, ny) in unclaimed
        in_res = (nx, ny) in resources

        dist_self = man(nx, ny, ox, oy)
        dist_now = man(x, y, ox, oy)

        # Prefer secure frontier expansion; if close, also consider flipping opponent cells.
        score = 0
        score += 6 * adj_self
        score += 2 * adj_un
        score += (4 if in_un else 0)
        score += (10 if in_res else 0)
        score += (-2 * adj_opp)
        if in_self:
            score += 1
        if in_opp:
            # Flipping helps most when it reduces opponent adjacency and we can pull away.
            score += 7 + (2 * adj_self) - (3 * adj_opp)
            score += (2 if dist_self > dist_now else -1)

        if near_opp:
            # When adjacent/near, avoid getting "surrounded": seek distance unless it enables a flip.
            score += (3 if dist_self > dist_now else -2)
        else:
            # Otherwise, keep moving generally toward open territory rather than chasing.
            score += (-1 * man(nx, ny, w // 2, h // 2))

        # Deterministic tie-break via lexicographic dir order already fixed.
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move