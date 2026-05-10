def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    # resources = set(map(tuple, observation.get("resources", [])))  # not used (resources per game: 0)

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
    dirs.sort()  # deterministic tie-break

    best_move = [0, 0]
    best_score = -10**9

    # Prefer expanding our connected frontier while contesting opponent cells safely.
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_self = adj_count(nx, ny, self_ter)
        adj_opp = adj_count(nx, ny, opp_ter)
        adj_un = adj_count(nx, ny, unclaimed)

        in_self = (nx, ny) in self_ter
        in_opp = (nx, ny) in opp_ter
        in_un = (nx, ny) in unclaimed

        # Safety: don't step too deep into opponent territory.
        safety = 2 * adj_self - 3 * adj_opp
        # Expansion: reward unclaimed adjacency and own adjacency.
        expand = 2 * adj_self + 1.5 * adj_un
        # If entering opponent territory, allow only when we are well-supported.
        flip_aggression = 0
        if in_opp:
            flip_aggression = 6 * adj_self - 6 * max(adj_opp, 1)
        if in_un:
            flip_aggression = 2 * adj_self + 1.0 * adj_un
        if in_self:
            flip_aggression = 1.0 * adj_self

        # Encourage moving away from opponent when contested, else slightly toward.
        dist = abs(nx - ox) + abs(ny - oy)
        approach = -0.12 * dist if adj_opp <= adj_self + 1 else 0.12 * dist

        score = 2.2 * safety + 1.6 * expand + flip_aggression + approach

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move