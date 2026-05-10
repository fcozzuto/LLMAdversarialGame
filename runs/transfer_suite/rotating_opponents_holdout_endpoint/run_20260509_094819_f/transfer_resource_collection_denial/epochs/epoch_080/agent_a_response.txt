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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    tr = int(observation.get("turns_remaining", 0) or 0)
    best = None
    best_key = None

    for x, y in res:
        ds = abs(x - sx) + abs(y - sy)
        do = abs(x - ox) + abs(y - oy)
        # Prefer resources we're strictly closer to; if tied/behind, penalize.
        denom = max(1, tr + 1)
        urgency = (ds * 7 + do * 3) / denom
        closer_pen = 0 if ds < do else (2.5 if ds == do else 5.0)
        # Small tie-break by coordinates for determinism.
        key = (closer_pen + urgency, ds, do, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_move = [0, 0]
    best_md = None
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        md = abs(tx - nx) + abs(ty - ny)
        # Also reduce opponent ability: avoid stepping closer to their position.
        opp_close = abs(ox - nx) + abs(oy - ny)
        mkey = (md, -opp_close, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]
            best_md = md

    if best_md is None:
        return [0, 0]
    return best_move