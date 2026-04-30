def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not res:
        tx, ty = (w // 2, h // 2)
    else:
        # Materially different: target "swing" resources where we can arrive much sooner,
        # but also block-feel by preferring resources aligned away from opponent.
        best = None
        for rx, ry in res:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            swing = (do - ds)  # positive means we are closer
            away = (rx - ox) * (rx - sx) + (ry - oy) * (ry - sy)  # prefer direction that separates
            # deterministic tie-break: fewer steps for us first, then lexicographic
            val = (swing * 10 + away) * 1000 - ds
            cand = (val, -ds, rx, ry)
            if best is None or cand > best:
                best = cand
        tx, ty = best[2], best[3]

    # Choose move that maximizes improvement vs current target, with obstacle-avoid and "deny opponent"
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        swing_after = do2 - ds2
        # Deny: if opponent is closer to many other resources, discourage wandering toward them
        deny = 0
        if res:
            for rx, ry in res:
                if (rx, ry) == (tx, ty):
                    continue
                if md(ox, oy, rx, ry) + 0 >= md(sx, sy, rx, ry):
                    # approximate: being closer to that resource reduces our deny, so penalize
                    if md(nx, ny, rx, ry) < md(sx, sy, rx, ry):
                        deny -= 1
        # Slightly prefer reducing distance to target and increasing distance from opponent
        score = (swing_after * 100) - ds2 - md(nx, ny, ox, oy) * 2 + deny
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]