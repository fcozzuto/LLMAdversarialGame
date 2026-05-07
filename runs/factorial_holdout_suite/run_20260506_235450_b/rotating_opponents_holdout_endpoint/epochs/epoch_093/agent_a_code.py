def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for ob in obstacles:
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            x, y = int(ob[0]), int(ob[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    turns_remaining = int(observation.get("turns_remaining", 0) or 0)

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    def parse_xy(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict):
            if "x" in r and "y" in r:
                return int(r["x"]), int(r["y"])
            if "position" in r:
                p = r["position"]
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    return int(p[0]), int(p[1])
        return None

    res = []
    for r in resources:
        p = parse_xy(r)
        if p is None:
            continue
        x, y = p
        if 0 <= x < w and 0 <= y < h:
            res.append((x, y))
    if not res:
        return [0, 0]

    best_move = [0, 0]
    best_val = None

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    speed_weight = 2 if turns_remaining else 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        my_best = 10**9
        opp_best = 10**9
        for tx, ty in res:
            md = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            if md < my_best:
                my_best = md
            if od < opp_best:
                opp_best = od

        # Prefer moves that reduce my distance to some resource, and also avoid letting opponent be closer.
        val = my_best * speed_weight - 2 * opp_best
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move