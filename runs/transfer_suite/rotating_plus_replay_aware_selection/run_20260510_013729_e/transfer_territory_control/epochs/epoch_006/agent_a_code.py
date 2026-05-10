def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cell_score(nx, ny):
        if (nx, ny) in obs or not inb(nx, ny):
            return -10**9
        base = 0
        if (nx, ny) in opp_ter:
            base += 6.0
        elif (nx, ny) in unclaimed:
            base += 3.0
        elif (nx, ny) in self_ter:
            base += 0.5

        md_opp = abs(nx - ox) + abs(ny - oy)
        md_self = abs(nx - x) + abs(ny - y)
        base += 1.5 * (md_opp - md_self)  # prefer moves that are relatively closer to where we can pressure
        # prefer approaching center (opponent tends to claim center)
        dist_center = abs(nx - cx) + abs(ny - cy)
        base += 2.0 * (-dist_center)
        # prefer cutting near opponent boundary (adjacent to their territory)
        for dx, dy in dirs:
            ax, ay = nx + dx, ny + dy
            if (ax, ay) in opp_ter:
                base += 2.0
                break
        return base

    best = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        sc = cell_score(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
        elif sc == best_sc:
            # deterministic tie-break: keep, then x+, then y+, then lex order
            cand = [dx, dy]
            if cand == [0, 0]:
                best = cand
            elif best != [0, 0]:
                if (dx, dy) < (best[0], best[1]):
                    best = cand

    return [int(best[0]), int(best[1])]