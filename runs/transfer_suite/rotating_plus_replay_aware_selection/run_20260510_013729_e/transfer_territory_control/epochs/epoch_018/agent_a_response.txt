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

    def nearest_dist(cellset, nx, ny):
        best = 10**9
        for cx, cy in cellset:
            d = abs(cx - nx) + abs(cy - ny)
            if d < best:
                best = d
        return best if cellset else best

    center = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = [0, 0]
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_self = adj_count(nx, ny, self_ter)
        adj_opp = adj_count(nx, ny, opp_ter)
        is_unclaimed = (nx, ny) in unclaimed
        is_opp = (nx, ny) in opp_ter
        is_res = (nx, ny) in resources

        # Encourage expansion (capture unclaimed, pressure opponent), but avoid over-committing into opponent blobs.
        sc = 0
        sc += 18 if is_unclaimed else 0
        sc += 12 if is_opp else 0  # flipping on entry
        sc += 4 * adj_self
        sc -= 6 * adj_opp
        sc += 3 * (8 - abs(nx - center[0]) - abs(ny - center[1])) / 8.0  # move toward center
        sc += 1.5 * (8 - (abs(nx - ox) + abs(ny - oy))) / 8.0  # pressure opponent
        if is_res:
            sc += 5

        # Prefer closeness to unclaimed targets early/midgame.
        unclaimed_list = observation.get("unclaimed_cells", []) or []
        if unclaimed_list:
            sc += 0.9 * (1.0 / (1 + nearest_dist(unclaimed_list, nx, ny)))

        # Deterministic tie-breaker: lexicographically smallest move (in dirs order by scoring then index).
        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]
    return best_move