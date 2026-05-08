def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        for dx, dy in moves[1:]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = (float("-inf"), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if (nx, ny) in self_set:
            base = 0.5
        elif (nx, ny) in unc_set:
            base = 2.5
        elif (nx, ny) in opp_set:
            base = 3.0
        else:
            base = 1.0
        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_self = abs(nx - (w - 1)) + abs(ny - (h - 1))  # drive toward our corner (opposite start)
        score = base + 0.02 * (dist_opp) - 0.01 * (dist_self)
        # small tiebreak: prefer staying near our territory edge to reduce risky wandering
        score += 0.03 * (1 if (nx, ny) in self_set else 0) - 0.01 * (1 if (nx, ny) in opp_set else 0)
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]