def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def parse_pos(p):
        if isinstance(p, dict):
            x = p.get("x", p.get("X", None))
            y = p.get("y", p.get("Y", None))
            if x is None or y is None:
                return None
            return int(x), int(y)
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        return None

    resources = observation.get("resources", []) or []
    rpos = []
    for r in resources:
        rp = parse_pos(r)
        if rp is not None:
            x, y = rp
            if in_bounds(x, y) and not blocked(x, y):
                rpos.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    def score_cell(x, y):
        if blocked(x, y):
            return None
        if rpos:
            # Greedy: closer to nearest resource than opponent
            myd = 10**9
            opd = 10**9
            for rx, ry in rpos:
                d = (x - rx) * (x - rx) + (y - ry) * (y - ry)
                if d < myd:
                    myd = d
                do = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
                if do < opd:
                    opd = do
            return (opd - myd) * 1000 - myd
        else:
            # No resources: move away from opponent
            myd = (x - ox) * (x - ox) + (y - oy) * (y - oy)
            return myd

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if sc is None:
            continue
        if best is None or sc > best_score or (sc == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = sc

    if best is None:
        # Fallback deterministic: stay if possible, else first valid neighbor
        if in_bounds(sx, sy) and not blocked(sx, sy):
            return [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and not blocked(nx, ny):
                return [dx, dy]
    return [best[0], best[1]]