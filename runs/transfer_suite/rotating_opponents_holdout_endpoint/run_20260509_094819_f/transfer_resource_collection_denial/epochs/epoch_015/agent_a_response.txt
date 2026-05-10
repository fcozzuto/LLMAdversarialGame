def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                res.append((rx, ry))
    if not res:
        return [0, 0]

    # Pick a resource we are likely to contest: maximize (opp_dist - self_dist), then minimize self_dist.
    best = None
    best_key = None
    for rx, ry in res:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (do - ds, -ds)  # higher first component, then smaller ds => more negative -ds
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Candidate move scoring with obstacle "safety" and progress.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = man(nx, ny, tx, ty)
        no = man(nx, ny, ox, oy)
        # Safety: penalize being closer to obstacles.
        if obst:
            min_ob = 10**9
            for ex, ey in obst:
                d = man(nx, ny, ex, ey)
                if d < min_ob:
                    min_ob = d
        else:
            min_ob = 10**9
        safety_pen = 0
        if min_ob <= 1:
            safety_pen = 3
        elif min_ob == 2:
            safety_pen = 1

        # Prefer direct progress, and secondarily increase opponent distance.
        key = (-ns, no, safety_pen, dx, dy)
        candidates.append((key, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]