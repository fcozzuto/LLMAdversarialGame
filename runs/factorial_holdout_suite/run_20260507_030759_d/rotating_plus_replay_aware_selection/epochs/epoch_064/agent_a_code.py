def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(ax, ay, bx, by):
        return max(abs(bx - ax), abs(by - ay))  # Chebyshev

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = None  # (priority tuple, move)
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue
        move_best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ot = dist(ox, oy, rx, ry)
            st = dist(nsx, nsy, rx, ry)
            # prefer resources we can arrive no later than opponent; tie-break by sooner
            # and then by margin (opponent later), and then by absolute distance for sanity
            if st <= ot:
                key = (0, st, ot - st, dist(sx, sy, rx, ry))
            else:
                # if we can't beat, still consider being close but avoid letting opponent take earlier
                key = (1, st - ot, st, dist(sx, sy, rx, ry))
            if move_best is None or key < move_best[0]:
                move_best = (key, rx, ry, st, ot)
        if move_best is None:
            continue
        if best is None or move_best[0] < best[0]:
            best = (move_best[0], [mdx, mdy])

    if best is None:
        # fallback: safest move (stay if blocked)
        for mdx, mdy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            if inb(sx + mdx, sy + mdy):
                return [mdx, mdy]
        return [0, 0]
    return best[1]