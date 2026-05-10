def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    opp_list = list(opp_terr) if opp_terr else [(int(ox), int(oy))]

    def adj4(x, y, S):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in S:
                c += 1
        return c

    def dist_to_nearest(x, y, pts):
        best = 10**9
        for px, py in pts:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    # Choose a target "frontier" direction: unclaimed cells adjacent to opponent territory (if any)
    frontier = []
    for ux, uy in unclaimed:
        if adj4(ux, uy, opp_terr) > 0:
            frontier.append((ux, uy))
    if frontier:
        tx, ty = min(frontier, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[1], p[0]))
    else:
        # otherwise head toward unclaimed with some notion of openness (away from obstacles)
        candidates = list(unclaimed) if unclaimed else [(sx, sy)]
        tx, ty = min(candidates, key=lambda p: (dist_to_nearest(p[0], p[1], opp_list) + abs(p[0] - sx) + abs(p[1] - sy), p[1], p[0]))

    # Evaluate each legal move (engine clips illegal by obstacle, but we also avoid obvious obstacles)
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_terr:
            base = 0.0
        elif (nx, ny) in opp_terr:
            base = 6.0  # strong incentive to flip opponent territory
        else:
            base = 3.5  # unclaimed/openness
        own_adj = adj4(nx, ny, self_terr)
        opp_adj = adj4(nx, ny, opp_terr)

        d_front = abs(tx - nx) + abs(ty - ny)
        d_opp = dist_to_nearest(nx, ny, opp_list)

        # Prefer tightening our connected area, reduce opponent adjacency, and move toward frontier
        val = base + 1.6 * own_adj - 2.2 * opp_adj + 0.9 * (d_opp * -1.0) + 0.8 * (40 - d_front) / 40.0
        # Tie-break deterministically toward (0,0), then lexicographically
        if val > best_val + 1e-9 or (abs(val - best_val) <= 1e-9 and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]