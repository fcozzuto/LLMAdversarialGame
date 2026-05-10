def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    px, py = observation["opponent_position"]

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Precompute nearest targets (deterministically)
    def nearest_cell(cells, x, y):
        best = None
        bestd = 10**9
        for cx, cy in cells:
            d = abs(cx - x) + abs(cy - y)
            if d < bestd or (d == bestd and (cx, cy) < best):
                bestd = d
                best = (cx, cy)
        return best, bestd

    target_u, du = nearest_cell(unclaimed, sx, sy) if unclaimed else (None, 10**9)
    target_o, do = nearest_cell(opp_terr, sx, sy) if opp_terr else (None, 10**9)

    # Heuristic weights
    for_scale = 0.0
    turn = int(observation.get("turn_index", 0))
    if du > 0:
        for_scale = 1.0
    leader = 1 if (turn % 10 == 9) else 0  # last of 10 before bonus could swing; be slightly more aggressive

    best_move = (0, 0)
    bestv = -10**18

    def cell_value(x, y):
        if not free(x, y):
            return -10**15
        if (x, y) in self_terr:
            base = 2.0
        elif (x, y) in unclaimed:
            base = 9.0
        elif (x, y) in opp_terr:
            base = 7.0
        else:
            base = 1.0

        # Prefer moving to cells that expand toward nearest unclaimed, else toward opponent
        d_to_u = abs(x - target_u[0]) + abs(y - target_u[1]) if target_u else 999
        d_to_o = abs(x - target_o[0]) + abs(y - target_o[1]) if target_o else 999
        toward = 0.0
        if target_u:
            toward += (du - d_to_u) * (4.0 + 0.5 * for_scale)
        else:
            toward += (do - d_to_o) * (2.5 + 0.5 * leader)

        # Avoid tight regions near opponent head/territory edges (reduce being swept)
        opp_dist = abs(x - px) + abs(y - py)
        adj_opp = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_terr:
                adj_opp += 1
        risk = 0.0
        if opp_dist <= 2:
            risk += (3 - opp_dist) * 2.0
        risk += adj_opp * 0.8

        # Tiny preference for staying away from obstacles via move validity already; also keep progress
        progress = -0.02 * (abs(x - sx) + abs(y - sy))

        return base + toward + progress - risk

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = cell_value(nx, ny)
        if v > bestv or (v == bestv and (dx, dy) < best_move):
            bestv = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]