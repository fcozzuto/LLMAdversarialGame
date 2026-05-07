def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or (0, 0)
    o = observation.get("opponent_position") or (0, 0)
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer winning races: target where we are closer than opponent; if losing, still contest if close.
    best = None
    best_key = None
    for tx, ty in resources:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        win_margin = do - ds  # positive if we are closer
        # Add a small bias to shorter paths, and to resources further along the line to opponent.
        along = (tx - sx) * (ox - sx) + (ty - sy) * (oy - sy)
        key = (1 if win_margin >= 0 else 0, win_margin, -ds, along)
        if best is None or key > best_key:
            best, best_key = (tx, ty), key

    tx, ty = best
    # Choose the best immediate move by minimizing distance-to-target with obstacle safety and tie-breakers.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        # Encourage moves that also reduce opponent's distance to that target (denial).
        do = man(ox, oy, tx, ty)
        v = (0, -d, -max(0, do - d), -abs((nx - ox)) - abs((ny - oy)))
        if bestm is None or v > bestv:
            bestm, bestv = [dx, dy], v

    if bestm is None:
        return [0, 0]
    return bestm