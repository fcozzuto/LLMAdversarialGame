def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    oppT = toset(observation.get("opponent_territory"))

    if not unclaimed and resources:
        unclaimed = set(resources)
    if not unclaimed:
        # Steal near opponent territory if possible
        cand = set()
        for (tx, ty) in oppT:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = tx + dx, ty + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                        cand.add((nx, ny))
        if not cand:
            return [0, 0]
        unclaimed = cand

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer central claims, but only if we can contest (closer than opponent).
    best = None
    bestv = -10**18
    for tx, ty in unclaimed:
        if (tx, ty) in obstacles:
            continue
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        if ds == 0 and (tx, ty) in oppT:
            v = 10000
        else:
            # contest term: positive when we are closer
            center = -0.12 * (abs(tx - cx) + abs(ty - cy))
            contest = (do - ds)
            edge_pen = -0.08 * (min(tx, w - 1 - tx) + min(ty, h - 1 - ty) < 1)
            v = 2.8 * contest + center + edge_pen - 0.03 * ds
        if v > bestv or (v == bestv and (best is None or (tx, ty) < best)):
            bestv = v
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If blocked, step to the best reachable neighbor by the same score.
    if (sx + dx, sy + dy) in obstacles:
        chosen = (0, 0)
        chosen_v = -10**18
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            # Evaluate one-step progress toward target and contest.
            ns = md(nx, ny, tx, ty)
            no = md(ox, oy, tx, ty)
            v = -ns + 0.25 * (no - ns)
            if v > chosen_v or (v == chosen_v and (mx, my) < chosen):
                chosen_v = v
                chosen = (mx, my)
        return [int(chosen[0]), int(chosen[1])]
    return [int(dx), int(dy)]