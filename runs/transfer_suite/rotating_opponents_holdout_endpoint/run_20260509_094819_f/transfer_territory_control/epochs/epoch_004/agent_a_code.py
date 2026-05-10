def choose_move(observation):
    x, y = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def min_dist_to_set(cx, cy, cell_set):
        md = 10**9
        for tx, ty in cell_set:
            d = abs(tx - cx) + abs(ty - cy)
            if d < md:
                md = d
        return md if cell_set else 10**6

    def neigh_score(nx, ny):
        neigh = 0
        u_adj = 0
        o_adj = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            tx, ty = nx + dx, ny + dy
            if (tx, ty) in self_terr:
                neigh += 2
            if (tx, ty) in unclaimed:
                u_adj += 3
            if (tx, ty) in opp_terr:
                o_adj += 1
        return neigh + u_adj - 2 * o_adj

    best = [0, 0]
    best_sc = -10**18

    opp_list = list(opp_terr)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0

        if (nx, ny) in unclaimed:
            sc += 70
        elif (nx, ny) in opp_terr:
            sc += 22  # allowed flipping, but prefer safer expansion first
        elif (nx, ny) in self_terr:
            sc += 8

        sc += neigh_score(nx, ny)

        # Reduce chasing; keep distance from opponent unless we can take unclaimed quickly
        d_opp = min_dist_to_set(nx, ny, opp_list)
        sc += (d_opp if (nx, ny) in opp_terr else 0.3 * d_opp)

        if (nx, ny) in unclaimed:
            sc += 0.5 * (observation.get("unclaimed_cells", []) is not None)

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best