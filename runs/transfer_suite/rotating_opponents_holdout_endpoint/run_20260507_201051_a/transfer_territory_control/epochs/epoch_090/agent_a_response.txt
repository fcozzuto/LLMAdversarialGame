def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    self_set = {(int(x), int(y)) for x, y in self_t}
    opp_set = {(int(x), int(y)) for x, y in opp_t}
    unc_set = {(int(x), int(y)) for x, y in unclaimed}

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    dirs8 = moves[1:]
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if (nx, ny) in unc_set:
            base = 6
        elif (nx, ny) in self_set:
            base = 2
        elif (nx, ny) in opp_set:
            base = -2
        else:
            base = 1  # should be rare, but treat as neutral

        adj_unc = 0
        for ax, ay in dirs8:
            ex, ey = nx + ax, ny + ay
            if ok(ex, ey) and (ex, ey) in unc_set:
                adj_unc += 1

        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)

        score = base + 0.7 * adj_unc + 0.15 * (16 - d_opp) - 0.10 * d_center
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]