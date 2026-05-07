def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w); h = int(h)
    except:
        w = 8; h = 8

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                x = int(x); y = int(y)
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            try:
                x = int(x); y = int(y)
            except:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        ay = b - d
        if ay < 0:
            ay = -ay
        return ax + ay

    best = None
    best_score = None
    for tx, ty in resources:
        sd = man(tx, ty, sx, sy)
        od = man(tx, ty, ox, oy)
        diff = od - sd
        # Prefer being able to arrive no later; within that, larger denial; else closer.
        if diff >= 0:
            score = (0, -diff, sd, tx + 31 * ty)
        else:
            score = (1, sd, od, tx + 31 * ty)
        if best_score is None or score < best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best
    candidates = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    # Deterministic tie-break: fixed order, prefer axis that reduces manhattan to target.
    best_move = [0, 0]
    best_d = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = man(tx, ty, nx, ny)
            if best_d is None or d < best_d:
                best_d = d
                best_move = [dx, dy]
    return best_move