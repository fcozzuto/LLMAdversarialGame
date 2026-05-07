def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def turns(ax, ay, bx, by):
        return max(abs(bx - ax), abs(by - ay))

    best_mv = (0, 0)
    best_key = None
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        # Choose the resource we are most likely to collect first; evaluate move by best such resource.
        move_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ot = turns(ox, oy, rx, ry)
            st = turns(nsx, nsy, rx, ry)
            if st > ot:
                # Still consider, but heavily penalize being later.
                key = (-10**6 + (ot - st), -st, rx, ry)
            else:
                # Prefer earlier or equal arrival, then closer.
                key = ((ot - st), -st, -abs(rx - nsx) - abs(ry - nsy), rx, ry)
            if move_best is None or key > move_best:
                move_best = key

        if move_best is None:
            continue
        if best_key is None or move_best > best_key:
            best_key = move_best
            best_mv = (mdx, mdy)

    return [int(best_mv[0]), int(best_mv[1])]