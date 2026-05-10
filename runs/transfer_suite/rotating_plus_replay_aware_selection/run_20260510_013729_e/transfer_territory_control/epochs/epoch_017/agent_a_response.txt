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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        in_self = (nx, ny) in self_ter
        in_opp = (nx, ny) in opp_ter
        in_uncl = (nx, ny) in unclaimed
        in_res = (nx, ny) in resources

        a_self = adj_count(nx, ny, self_ter)
        a_opp = adj_count(nx, ny, opp_ter)

        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_ctr = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)

        score = 0.0
        score += 2.5 * a_self
        score -= 2.0 * a_opp

        if in_res:
            score += 6.0
        if in_self:
            score += 1.0
        if in_uncl:
            score += 4.0 + 0.2 * a_self
        if in_opp:
            score += 7.5 - 1.5 * a_opp  # invade only when not surrounded by opponent

        # Keep pressure: prefer moves that reduce distance to opponent slightly, but avoid walking into their mass.
        score += 0.6 * (7 - dist_opp) - 0.2 * dist_ctr

        # Strongly prefer moves that extend frontier (unclaimed adjacent area)
        score += 0.8 * adj_count(nx, ny, unclaimed)

        # Deterministic tie-break: lexicographic preference via ordered dirs already set.
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]