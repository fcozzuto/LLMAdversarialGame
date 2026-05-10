def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def score_cell(nx, ny):
        if (nx, ny) in obstacles:
            return -10**18
        if (nx, ny) in self_set:
            gain = 0
        elif (nx, ny) in opp_set:
            gain = 1
        elif (nx, ny) in unclaimed:
            gain = 1
        else:
            gain = 1  # unspecified/rare: treat as potential
        # center and approach unclaimed/frontier
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.02
        # avoid moving into opponent's immediate neighborhood
        opp_dist = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        opp_pen = 2000.0 / (1.0 + opp_dist)
        # prefer moving toward nearest unclaimed (or toward opponent-edges if none)
        frontier_targets = unclaimed if unclaimed else list(opp_set)
        best_d = None
        for tx, ty in frontier_targets:
            if (tx, ty) in obstacles:
                continue
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if best_d is None or d < best_d:
                best_d = d
        approach = 0 if best_d is None else -best_d * 0.001
        return gain * 10000.0 + center + approach - opp_pen

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_cell(nx, ny)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]