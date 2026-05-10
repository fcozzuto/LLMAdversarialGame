def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    sx, sy = int(sx), int(sy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Precompute nearest targets (deterministic, bounded)
    def nearest_dist(points, x, y):
        if not points:
            return 10**9
        best = 10**9
        for px, py in points:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    du = nearest_dist(unclaimed, sx, sy)
    do = nearest_dist(list(opp_terr) if opp_terr else [], sx, sy)
    dcenter = abs(sx - cx) + abs(sy - cy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic rotation to reduce loops
    rot = int(observation.get("turn_index", 0)) % 9
    dirs = dirs[rot:] + dirs[:rot]

    best_move = [0, 0]
    best_score = -10**18

    # Heuristic weights tuned for greedy territory control
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            score = -10**12
        else:
            score = 0.0
            # Prefer moving onto new/unclaimed/opp-owned territory
            if (nx, ny) in self_terr:
                score += 5.0
            elif (nx, ny) in opp_terr:
                score += 35.0
            elif (nx, ny) in set(unclaimed):
                score += 45.0
            else:
                score += 10.0  # neutral cell

            # Distance pressure: grab nearest unclaimed; then disrupt opponent
            if unclaimed:
                dnu = nearest_dist(unclaimed, nx, ny)
                score += (du - dnu) * 4.0
            if opp_terr:
                dno = nearest_dist(list(opp_terr), nx, ny)
                score += (do - dno) * 2.5

            # Center pressure to fight center-claimer tendency
            dnc = abs(nx - cx) + abs(ny - cy)
            score += (dcenter - dnc) * 3.0

            # Slightly favor forward progress relative to opponent corner (opponent position)
            ox, oy = observation["opponent_position"]
            ox, oy = int(ox), int(oy)
            dp_prev = abs(sx - ox) + abs(sy - oy)
            dp_new = abs(nx - ox) + abs(ny - oy)
            score += (dp_prev - dp_new) * 1.5

        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]