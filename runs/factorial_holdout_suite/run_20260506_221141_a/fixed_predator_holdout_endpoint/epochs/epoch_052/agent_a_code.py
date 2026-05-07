def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
        except Exception:
            pass

    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]

    # Pick target that favors collecting first while denying opponent.
    best_target = None
    best_tscore = -10**18
    for t in resources:
        sd = md((sx, sy), t)
        od = md((ox, oy), t)
        # Larger is better: make opponent farther and self closer; slight tie-break for immediacy.
        tscore = (od - sd) * 1000 - sd
        if tscore > best_tscore or (tscore == best_tscore and (t[0], t[1]) < (best_target[0], best_target[1])):
            best_tscore = tscore
            best_target = t

    tx, ty = best_target

    # Choose best immediate move (handles obstacle blocking / diagonal preference).
    best_move = (0, 0)
    best_mscore = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        # Evaluate against the chosen target, plus an optional nearby-resource nudge.
        sd = md((nx, ny), (tx, ty))
        od = md((ox, oy), (tx, ty))
        mscore = (od - sd) * 1000 - sd
        # If multiple resources, encourage moving toward any that's competitive.
        for t in resources:
            if md((nx, ny), t) <= sd + 1:
                sd2 = md((nx, ny), t)
                od2 = md((ox, oy), t)
                mscore = max(mscore, (od2 - sd2) * 1000 - sd2 - 1)
        if mscore > best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)
        elif mscore == best_mscore:
            # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying still last.
            cand = (dx, dy)
            if cand < best_move:
                best_move = cand

    return [int(best_move[0]), int(best_move[1])]