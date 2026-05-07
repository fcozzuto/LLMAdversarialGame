def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []

    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for r in resources:
        tx, ty = int(r[0]), int(r[1])
        if inside(tx, ty) and not blocked(tx, ty):
            valid.append((tx, ty))
    if not valid:
        return [0, 0]

    scored = []
    for tx, ty in valid:
        od = man(ox, oy, tx, ty)
        sd = man(sx, sy, tx, ty)
        scored.append((od, sd, tx, ty))
    scored.sort(key=lambda t: (t[0], t[2], t[3]))  # opponent nearest first, deterministic tie-break

    topk = scored[:min(3, len(scored))]
    # Target a resource the opponent is likely to take next (not necessarily the nearest).
    # Choose among topk the one we can reach the quickest.
    best = None
    for od, sd, tx, ty in topk:
        key = (sd, abs(tx - sx) + abs(ty - sy), tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    _, (tx, ty) = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                cand.append((0, 0))
            else:
                nx, ny = sx + mx, sy + my
                if inside(nx, ny) and not blocked(nx, ny):
                    cand.append((mx, my))
    cand.sort(key=lambda m: (-(m[0] * (1 if tx > sx else -1) if m[0] != 0 else 0) - (m[1] * (1 if ty > sy else -1) if m[1] != 0 else 0),
                              man(sx + m[0], sy + m[1], tx, ty), m[0], m[1]))

    primary = (dx, dy)
    if primary in cand:
        return [dx, dy]
    for mx, my in cand:
        return [mx, my]
    return [0, 0]