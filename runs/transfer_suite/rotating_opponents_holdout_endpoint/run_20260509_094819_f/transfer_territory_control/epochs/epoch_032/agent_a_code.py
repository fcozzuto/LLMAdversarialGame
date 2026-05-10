def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    myc = int(observation.get("self_territory_count", len(selfT)))
    oppc = int(observation.get("opponent_territory_count", len(oppT)))
    behind = 1 if myc < oppc else 0
    risk = 18 if behind else 8  # if behind, take more opponent entries

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def min_dist2_to_set(x, y, S):
        best = 10**9
        for (tx, ty) in S:
            dx = tx - x
            dy = ty - y
            d = dx * dx + dy * dy
            if d < best:
                best = d
        return best

    opp_list = list(oppT)
    un_list = list(unclaimed)

    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in selfT:
            base = 28
        elif (nx, ny) in oppT:
            base = 120 + risk
        elif (nx, ny) in unclaimed:
            base = 72
        else:
            base = 12

        # Frontier pressure: move closer to opponent territory if available, else chase unclaimed
        if opp_list:
            d2_opp = min_dist2_to_set(nx, ny, opp_list)
            frontier = -2.5 * d2_opp
        else:
            d2_opp = 0
            if un_list:
                d2_un = min_dist2_to_set(nx, ny, set(un_list))
                frontier = -2.0 * d2_un
            else:
                frontier = 0

        # Keep somewhat toward center to reduce corner trapping
        dc2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        center = -0.35 * dc2
        val = base + frontier + center

        if val > best_val or (val == best_val and (dx == 0 and dy == 0)):
            best_val = val
            best_move = [dx, dy]

    return best_move