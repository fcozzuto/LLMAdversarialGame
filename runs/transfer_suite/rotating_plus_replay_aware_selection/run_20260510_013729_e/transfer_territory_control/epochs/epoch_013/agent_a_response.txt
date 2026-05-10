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

    def edge_bias(nx, ny):
        bx = min(nx, w - 1 - nx)
        by = min(ny, h - 1 - ny)
        return -(bx + by)  # prefer edges (safer for territorial sweeping)

    best_dxdy = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in resources:
            res_bonus = 50
        else:
            res_bonus = 0

        if (nx, ny) in opp_ter:
            flip_bonus = 40
        else:
            flip_bonus = 0

        if (nx, ny) in unclaimed:
            claim_bonus = 10
        else:
            claim_bonus = 0

        adj_self = adj_count(nx, ny, self_ter)
        adj_opp = adj_count(nx, ny, opp_ter)
        adj_uncl = adj_count(nx, ny, unclaimed)

        # Keep momentum away from getting surrounded by opponent territory
        trap_penalty = 8 if (adj_opp >= 5 and adj_self <= 1) else 0

        # Prefer moving toward opponent only when it increases border pressure
        to_opp = -abs(nx - ox) - abs(ny - oy)

        score = (adj_self * 7 + adj_uncl * 4 - adj_opp * 5 + flip_bonus + claim_bonus +
                 res_bonus + edge_bias(nx, ny) + to_opp + trap_penalty)

        if score > best_score:
            best_score = score
            best_dxdy = [dx, dy]

    return best_dxdy