def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = {tuple(p) for p in (observation.get("obstacles") or [])}
    self_set = {tuple(p) for p in (observation.get("self_territory") or [])}
    opp_set = {tuple(p) for p in (observation.get("opponent_territory") or [])}
    un_set = {tuple(p) for p in (observation.get("unclaimed_cells") or [])}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def adj_counts(x, y):
        own = opp = un = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if not (ddx or ddy):
                    continue
                ax, ay = x + ddx, y + ddy
                if 0 <= ax < w and 0 <= ay < h:
                    t = (ax, ay)
                    if t in self_set:
                        own += 1
                    elif t in opp_set:
                        opp += 1
                    elif t in un_set:
                        un += 1
        return own, opp, un

    best = None
    bestv = -10**18
    for dx, dy, x, y in cand:
        if (x, y) in opp_set:
            base = 14.0
        elif (x, y) in un_set:
            base = 6.0
        elif (x, y) in self_set:
            base = 1.5
        else:
            base = 2.0

        own_adj, opp_adj, un_adj = adj_counts(x, y)
        dist = abs(x - ox) + abs(y - oy)
        val = base + 1.1 * own_adj + 1.6 * opp_adj + 0.7 * un_adj + 0.08 * dist

        # slight bias to move when tie: prefer larger dist if not capturing enemy
        if best is None or val > bestv + 1e-9 or (abs(val - bestv) <= 1e-9 and ((x, y) not in opp_set) and dist > best[0]):
            bestv = val
            best = (dist, dx, dy)

    return [int(best[1]), int(best[2])]