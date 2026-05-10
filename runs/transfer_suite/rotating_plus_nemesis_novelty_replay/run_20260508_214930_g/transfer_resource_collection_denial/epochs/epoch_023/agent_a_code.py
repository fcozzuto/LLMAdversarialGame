def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    resset = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                resset.add((x, y))
    if not resset:
        return [0, 0]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # choose target resource by who reaches first (margin), then prefer nearer to center
    best = None
    for rx, ry in resset:
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        margin = oppd - myd
        center = abs(rx - cx) + abs(ry - cy)
        # prefer positive margin, then smaller myd, then smaller center, then deterministic hash
        key = (margin, -myd, -(-center), -(rx * 8 + ry))
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, None)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # score next step: immediate resource, improve win margin to target, also reduce distance to target
        immediate = 1 if (nx, ny) in resset else 0
        myd = man(nx, ny, tx, ty)
        oppd = man(ox, oy, tx, ty)
        margin = oppd - myd
        step_to_center = abs(nx - cx) + abs(ny - cy)
        # also discourage moving toward opponent to protect lead when close
        opp_close = -man(nx, ny, ox, oy)
        score = (immediate * 1000) + (margin * 10) - (myd) - (step_to_center) + (opp_close * 0.2)

        if best_move[0] is None or score > best_move[0]:
            best_move = (score, [dx, dy])

    return best_move[1] if best_move[1] is not None else [0, 0]