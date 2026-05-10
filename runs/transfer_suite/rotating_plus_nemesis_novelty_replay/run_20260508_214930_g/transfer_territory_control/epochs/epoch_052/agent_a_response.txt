def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a deterministic "priority" target direction to diversify when scores tie
    # without using randomness.
    idx = observation.get("turn_index", 0)
    bias = 1 if (idx % 2 == 0) else -1
    primary_pref = ((1 if ox > sx else -1 if ox < sx else 0), (1 if oy > sy else -1 if oy < sy else 0))
    if primary_pref == (0, 0):
        primary_pref = (bias, 0)

    # Precompute a couple of nearest targets to keep scoring cheap.
    # Use a small deterministic subset if many cells.
    un_list = list(unclaimed)
    opp_list = list(opp_t)
    if len(un_list) > 24:
        un_list = un_list[::max(1, len(un_list)//24)]
    if len(opp_list) > 16:
        opp_list = opp_list[::max(1, len(opp_list)//16)]

    base_dist_to_opp = abs(sx - ox) + abs(sy - oy)

    def nearest_dist(cells, x, y):
        if not cells:
            return 10**9
        best = 10**9
        for tx, ty in cells:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    dist_un = nearest_dist(un_list, sx, sy)
    dist_opp = nearest_dist(opp_list, sx, sy)

    best_move = (0, 0)
    best_score = -10**18

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0

        # High value for flipping or taking contested space
        if (nx, ny) in opp_t:
            score += 2500
        elif (nx, ny) in unclaimed:
            score += 120
        elif (nx, ny) in self_t:
            score += 8
        else:
            score += 0

        # Encourage moving toward useful areas: unclaimed first, then opponent territory
        nd_un = nearest_dist(un_list, nx, ny)
        nd_opp = nearest_dist(opp_list, nx, ny)
        score += (dist_un - nd_un) * 7
        score += (dist_opp - nd_opp) * 5

        # Keep some pressure toward opponent position without overcommitting to a straight line
        d_now = abs(nx - ox) + abs(ny - oy)
        score += (base_dist_to_opp - d_now) * 2

        # Prefer staying on/near our territory only lightly; avoid tunneling
        if (nx, ny) in self_t:
            score -= 2
        # Small tie-breaker: align with primary preference direction
        score += (ddx * primary_pref[0] + ddy * primary_pref[1]) * 0.5

        # Deterministic tie-break: consistent ordering in dirs, plus exact score
        if score > best_score + 1e-9:
            best_score = score
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]