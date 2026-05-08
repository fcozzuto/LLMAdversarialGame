def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y):
                obs_set.add((x, y))
        except:
            pass

    opp_terr = observation.get("opponent_territory", []) or []
    opp_set = set()
    for p in opp_terr:
        try:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y):
                opp_set.add((x, y))
        except:
            pass

    un_cells = observation.get("unclaimed_cells", None)
    if un_cells is None:
        un_cells = observation.get("resources", None) or []
    un_set = []
    for p in un_cells:
        try:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y) and (x, y) not in obs_set and (x, y) != (sx, sy):
                un_set.append((x, y))
        except:
            pass

    terr_cmp = int(observation.get("self_territory_count", 0) or 0) - int(observation.get("opponent_territory_count", 0) or 0)
    counterclaim = terr_cmp < 0

    opp_target = None
    if opp_set:
        # nearest opponent territory cell
        opp_target = min(opp_set, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))

    un_target = None
    if un_set:
        un_target = min(un_set, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))

    moves = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue

        score = 0
        if (nx, ny) in opp_set:
            score += 100000  # immediate counterclaim
        if opp_target is not None:
            score += (- (abs(nx - opp_target[0]) + abs(ny - opp_target[1])) ) * (3 if counterclaim else 1)
        if un_target is not None:
            score += (- (abs(nx - un_target[0]) + abs(ny - un_target[1])) ) * (1 if counterclaim else 2)

        # small tie-breaker: prefer moving closer to opponent position when behind
        if counterclaim:
            score += - (abs(nx - ox) + abs(ny - oy)) * 0.1

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best