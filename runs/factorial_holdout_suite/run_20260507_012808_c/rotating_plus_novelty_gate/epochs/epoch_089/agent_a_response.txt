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

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prefer resources where we are closer than the opponent; otherwise still race nearest.
    best = None
    for tx, ty in resources:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        advantage = do - ds  # higher is better (we want positive)
        # Tie-break: prefer smaller ds, then larger do (opponent farther), then a stable ordering
        key = (advantage, -ds, do, -tx, -ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Step greedily toward target, but avoid letting opponent get substantially closer if possible.
    bestm = None
    for dx, dy, nx, ny in moves:
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        # Additional local bias: keep within target direction; reduce distance, and reduce deviation from (tx,ty).
        dist_now = md(sx, sy, tx, ty)
        progress = dist_now - ds2
        key = (progress, -(ds2), (do2 - ds2), -abs(nx - tx) - abs(ny - ty), -abs(dx) - abs(dy))
        if bestm is None or key > bestm[0]:
            bestm = (key, (dx, dy))
    return [int(bestm[1][0]), int(bestm[1][1])]