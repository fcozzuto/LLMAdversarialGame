def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    if not res:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a resource where we have the best "race" advantage; tie-break by smaller self distance.
    best = None
    for tx, ty in res:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        key = (od - sd, -sd, -tx, -ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for mx in (dx, 0, -dx):
        for my in (dy, 0, -dy):
            nx, ny = sx + mx, sy + my
            if (mx, my) == (0, 0) or True:
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    candidates.append((mx, my))
    # Deduplicate preserving order
    seen = set()
    uniq = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    candidates = uniq

    # Prefer move that reduces our distance to the target while keeping opponent from being closer after move.
    bestm = (None, None)
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        sd = abs(tx - nx) + abs(ty - ny)
        od = abs(tx - ox) + abs(ty - oy)
        score = (od - sd, -sd, -abs(tx - nx), -abs(ty - ny))
        if bestm[0] is None or score > bestm[0]:
            bestm = (score, (mx, my))

    mx, my = bestm[1]
    if mx is None:
        return [0, 0]
    return [int(mx), int(my)]