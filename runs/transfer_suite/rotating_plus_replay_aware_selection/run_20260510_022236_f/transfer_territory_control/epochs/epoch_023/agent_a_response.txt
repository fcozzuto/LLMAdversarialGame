def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    cx, cy = w // 2, h // 2
    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def neighbors8(x, y):
        res = []
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                res.append((nx, ny))
        return res

    if unclaimed:
        best = None
        for tx, ty in unclaimed:
            adj_own = 0
            for nx, ny in neighbors8(tx, ty):
                if (nx, ny) in self_terr:
                    adj_own += 1
            dist_center = abs(tx - cx) + abs(ty - cy)
            # Push toward contested areas: close to opponent, but only if we can expand well.
            if opp_terr:
                dist_opp = min(abs(tx - ox) + abs(ty - oy) for (ox, oy) in opp_terr)
            else:
                dist_opp = 0
            # Tie-break deterministically by coordinates.
            score = (adj_own * 1000) - dist_opp * 3 - dist_center
            cand = (-score, tx, ty)
            if best is None or cand < best:
                best = cand
        _, tx, ty = best
    else:
        # No unclaimed: seek direct flips by moving toward nearest opponent cell.
        if not opp_terr:
            return [0, 0]
        tx, ty = min(opp_terr, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        # Deterministic fallback: choose the best neighboring move (still toward target).
        bestm = None
        for mx, my in neighbors8(sx, sy):
            md = abs(tx - mx) + abs(ty - my)
            cand = (md, mx, my)
            if bestm is None or cand < bestm:
                bestm = cand
        _, nx, ny = bestm
        dx, dy = nx - sx, ny - sy

    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    if dx == 0 and dy == 0:
        return [0, 0]
    return [int(dx), int(dy)]