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

    def neigh_free(nx, ny):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    c += 1
        return c

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

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_unclaimed = (nx, ny) in unclaimed
        is_opp = (nx, ny) in opp_ter
        is_self = (nx, ny) in self_ter

        adj_self = adj_count(nx, ny, self_ter)
        adj_opp = adj_count(nx, ny, opp_ter)

        d_op = abs(nx - ox) + abs(ny - oy)
        d_ctr = abs(nx - center_x) + abs(ny - center_y)

        score = 0.0
        score += 3.2 if is_opp else 0.0          # flipping into opponent territory
        score += 1.8 if is_unclaimed else 0.2 if is_self else 0.0
        score += 0.35 * adj_self               # keep strong local control
        score -= 0.25 * adj_opp               # avoid stepping into enemy clusters
        score += 0.06 * neigh_free(nx, ny)    # avoid getting boxed
        score += 0.05 * d_op                  # prefer increasing distance from opponent
        score -= 0.03 * d_ctr                # gently move toward center

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move