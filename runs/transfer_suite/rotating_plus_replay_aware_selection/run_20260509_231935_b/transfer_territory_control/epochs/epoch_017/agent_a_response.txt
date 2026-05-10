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
    order = list(dirs)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    def cell_type(x, y):
        t = 0
        if (x, y) in self_set:
            t = 1
        elif (x, y) in opp_set:
            t = 2
        elif (x, y) in un_set:
            t = 3
        return t

    best = None
    best_val = -10**18
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        t = cell_type(nx, ny)

        own_adj = 0
        opp_adj = 0
        un_adj = 0
        for px, py in neigh8(nx, ny):
            if (px, py) in self_set:
                own_adj += 1
            elif (px, py) in opp_set:
                opp_adj += 1
            elif (px, py) in un_set:
                un_adj += 1

        dist_opp_before = abs(sx - ox) + abs(sy - oy)
        dist_opp_after = abs(nx - ox) + abs(ny - oy)
        avoid = 0.0

        if t == 2:  # stepping into opponent territory flips; do only when we are well-anchored
            if own_adj >= 2:
                gain = 9.0
            elif own_adj == 1 and opp_adj >= 2:
                gain = -2.0
            else:
                gain = 1.0
        elif t == 3:  # expanding into unclaimed
            gain = 6.0
            if own_adj == 0 and opp_adj >= 1:
                gain -= 3.0
        else:  # our own territory or unknown
            gain = 1.0 if t == 1 else 0.5

        # Defensive posture: prefer increasing distance from opponent and moving toward strong self-frontier
        defend = (dist_opp_after - dist_opp_before) * 0.6
        frontier = own_adj * 1.2 + un_adj * 0.3 - opp_adj * 0.9

        # Mild preference to reduce churn: avoid moves that put us adjacent to too many opponent cells unless capturing
        churn_pen = 0.0
        if t != 2:
            churn_pen = max(0, opp_adj - 1) * 1.0

        val = gain + frontier + defend - churn_pen

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]