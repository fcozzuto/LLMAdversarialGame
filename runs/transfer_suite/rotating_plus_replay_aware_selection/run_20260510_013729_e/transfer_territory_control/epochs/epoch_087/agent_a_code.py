def choose_move(observation):
    gw = int(observation.get("grid_width") or 8)
    gh = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [gw - 1, gh - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = observation.get("self_territory") or []
    self_set = set()
    for p in self_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_set.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    cand = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obs:
                cand.append((x, y))

    if not cand:
        opp_t = observation.get("opponent_territory") or []
        for p in opp_t:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < gw and 0 <= y < gh and (x, y) not in obs:
                    cand.append((x, y))

    if not cand:
        return [0, 0]

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < gw and 0 <= ny < gh:
                    yield nx, ny

    opp_t = observation.get("opponent_territory") or []
    opp_set = set()
    for p in opp_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    best = None
    best_sc = None
    for x, y in cand:
        if (x, y) in self_set:
            continue
        md = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)

        adj_self = 0
        for nx, ny in neigh8(x, y):
            if (nx, ny) in self_set:
                adj_self += 1

        # If we step near opponent-controlled frontier, it helps to grab first.
        adj_opp = 0
        for nx, ny in neigh8(x, y):
            if (nx, ny) in opp_set:
                adj_opp += 1

        sc = 3 * adj_self + 1.0 * od - 2.5 * md - 0.6 * adj_opp
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (x, y)

    tx, ty = best if best is not None else (sx, sy)
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]