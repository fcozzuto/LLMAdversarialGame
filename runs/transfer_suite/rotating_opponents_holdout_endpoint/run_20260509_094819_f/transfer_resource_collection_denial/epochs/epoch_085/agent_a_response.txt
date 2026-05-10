def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def advantage(tx, ty):
        ds = man(tx, ty, sx, sy)
        do = man(tx, ty, ox, oy)
        return (do - ds, -ds)

    best_t = None
    best = None
    for t in res:
        adv = advantage(t[0], t[1])
        if best is None or adv > best or (adv == best and (t[0], t[1]) < (best_t[0], best_t[1])):
            best = adv
            best_t = t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tx, ty = best_t

    def cell_score(nx, ny):
        if (nx, ny) in obs:
            return None
        # Encourage moving toward the chosen target, but keep an eye on other resources to grab first.
        cur = (man(nx, ny, ox, oy) - man(nx, ny, sx, sy), -man(nx, ny, tx, ty))
        # Small deterministic bias to break ties
        return (cur, (nx, ny))

    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            sc = cell_score(nx, ny)
            if sc is None:
                continue
            if best_score is None or sc > best_score:
                best_score = sc
                best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]