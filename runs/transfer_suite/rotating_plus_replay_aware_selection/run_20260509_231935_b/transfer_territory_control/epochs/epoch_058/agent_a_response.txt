def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    t = int(observation.get("turn_index", 0))
    k = t % len(dirs)
    dirs = dirs[k:] + dirs[:k]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_type(x, y):
        p = (x, y)
        if p in self_terr:
            return 2
        if p in opp_terr:
            return 1
        return 0  # unclaimed

    if unclaimed:
        # Prefer center-ish and relatively contestable targets (closer than opponent).
        best = None
        best_key = None
        for x, y in unclaimed:
            if (x, y) in obstacles:
                continue
            key = (man(x, y, cx, cy), man(sx, sy, x, y) - man(ox, oy, x, y), x, y)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)
        tx, ty = best
    else:
        # If nothing to claim, press towards center and nearby opponent territory.
        tx, ty = cx, cy
        if opp_terr:
            near = sorted(list(opp_terr), key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
            tx, ty = near[0]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        c = cell_type(nx, ny)  # 2=self,1=opp,0=unclaimed
        dist_to_target = man(nx, ny, tx, ty)
        dist_from_opp = man(nx, ny, ox, oy)
        # Unclaimed is highest, then deny opponent territory, then self territory.
        base = 0
        if (nx, ny) in unclaimed:
            base = 300
        if (nx, ny) in opp_terr:
            base = 180
        if (nx, ny) in self_terr:
            base = 90
        # Central pressure and opponent distance (stay harder to contest).
        score = base - 6 * dist_to_target + 2 * dist_from_opp - 1.5 * man(nx, ny, cx, cy)
        # Mildly discourage stepping onto opponent far from target (commit only if aligned).
        if (nx, ny) in opp_terr and dist_to_target > 2:
            score -= 25
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]