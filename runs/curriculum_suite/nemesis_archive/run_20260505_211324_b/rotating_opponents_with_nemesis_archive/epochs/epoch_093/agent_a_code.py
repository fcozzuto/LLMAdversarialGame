def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not res:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    best = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d_self = md(nx, ny, ox, oy)
        # Maximize advantage to win a target, while slightly preferring staying closer to opponent to contest sweep.
        # If no clear advantage targets exist, this still aims for nearest.
        best_t = None
        best_adv = None
        for rx, ry in res:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            adv = (do - ds)  # positive means we are closer than opponent
            key = (adv, -ds)
            if best_t is None or key > best_t:
                best_t = key
                best_adv = adv

        adv = best_t[0]
        ds_best = -best_t[1]
        # Secondary preferences: avoid getting stuck; keep some distance from opponent unless we can secure resources.
        dist_pref = -d_self if adv > 0 else d_self
        # Deterministic tie-break by ordering via tuple comparisons
        cand_key = (adv, -ds_best, dist_pref, dx, dy)
        if best_key is None or cand_key > best_key:
            best_key = cand_key
            best = [dx, dy]

    return best