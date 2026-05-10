def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))
    un_set = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    options = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def nearest_dist(x, y, cells):
        best = 10**9
        for a, b in cells:
            d = abs(a - x) + abs(b - y)
            if d < best:
                best = d
        return best

    has_un = bool(un_set)
    has_opp = bool(opp_t)
    un_list = list(un_set) if has_un else []
    opp_list = list(opp_t) if has_opp else []

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0.0
        if (nx, ny) in un_set:
            score += 50.0
        elif (nx, ny) in opp_t:
            score += 15.0
        else:
            score += 1.0

        if has_un:
            score += 4.0 / (1 + abs(nx - sx) + abs(ny - sy))
            score += 12.0 / (1 + nearest_dist(nx, ny, un_list))
        if has_opp:
            score += 3.0 / (1 + nearest_dist(nx, ny, opp_list))

        # deterministic tie-break: smaller dx then dy
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move