def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]
    if not inb(sx, sy):
        # Try to recover deterministically
        for mdx, mdy in moves:
            nx, ny = sx + mdx, sy + mdy
            if inb(nx, ny):
                return [mdx, mdy]
        return [0, 0]

    def dist(ax, ay, bx, by):
        return max(abs(bx - ax), abs(by - ay))

    # Pick target resource that gives best advantage (or best closeness if no advantage).
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources we can reach strictly earlier; if not, still pick one that most reduces opponent lead.
        adv = od - sd
        key = (-(adv < 0), -(adv), sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), sd, od)

    if best is None:
        return [0, 0]
    (rx, ry) = best[1]

    # Greedy step: maximize advantage after move, break ties by minimizing self distance.
    best_mv = (0, 0)
    best_key = None
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue
        nsd = dist(nsx, nsy, rx, ry)
        nod = dist(ox, oy, rx, ry)
        nadv = nod - nsd
        # Small deterministic bias to reduce oscillation: prefer staying closer in x, then y.
        bias = abs(nsx - rx) + 0.1 * abs(nsy - ry)
        key = (-(nadv < 0), -(nadv), nsd, bias, mdx, mdy)
        if best_key is None or key < best_key:
            best_key = key
            best_mv = (mdx, mdy)

    return [int(best_mv[0]), int(best_mv[1])]