def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    unclaimed_set = set(unclaimed)
    opp_adj = set()
    for (x, y) in oppT:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) not in oppT:
                    opp_adj.add((nx, ny))
    frontier = [c for c in unclaimed if c in opp_adj] or [c for c in unclaimed if c not in selfT]
    if not frontier:
        # if no unclaimed, push toward opponent's territory
        frontier = [c for c in opp_adj if c not in selfT] or [tuple(observation.get("opponent_position"))]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # pick a deterministic target: closest frontier cell with tie-break favoring edge distance to opponent
    if frontier:
        tx, ty = min(frontier, key=lambda c: (man(c[0], c[1], sx, sy), man(c[0], c[1], ox, oy), c[0], c[1]))
    else:
        tx, ty = w // 2, h // 2

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        landing = (nx, ny)
        val = 0
        val += 6 if landing in unclaimed_set else 0
        val += 5 if landing in oppT else 0  # flipping on entry
        # bonus for moving toward target, penalize moving away
        val += -man(nx, ny, tx, ty)
        # local pressure: prefer positions adjacent to opponent territory or unclaimed
        adj_unclaimed = 0
        adj_opp = 0
        for ddx, ddy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h:
                if (ax, ay) in unclaimed_set:
                    adj_unclaimed += 1
                if (ax, ay) in oppT:
                    adj_opp += 1
        val += 2 * adj_unclaimed + 3 * adj_opp
        # mild safety to avoid stepping back into own territory if equally good
        if landing in selfT:
            val -= 0.5
        # deterministic tie-break
        key = (val, -man(nx, ny, ox, oy), nx, ny)
        if key > (best_val, 0, 0, 0):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]