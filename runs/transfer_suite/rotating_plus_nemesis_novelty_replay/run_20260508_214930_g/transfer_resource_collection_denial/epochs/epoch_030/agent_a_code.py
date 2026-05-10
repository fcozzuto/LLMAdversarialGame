def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    resset = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                resset.append((x, y))
    if not resset:
        # deterministic fallback: go to nearer center cell
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Two-mode interceptor/collector:
    # 1) Find the resource opponent is closest to (contested priority).
    # 2) If we can also beat it (strictly earlier), collect it.
    # 3) Otherwise, move to reduce our distance to it (intercept path),
    #    and in ties, prefer moves that keep Manhattan distance to that target decreasing.
    target = None
    best_oppd = None
    for rx, ry in resset:
        od = man(ox, oy, rx, ry)
        if best_oppd is None or od < best_oppd or (od == best_oppd and (rx, ry) < target):
            best_oppd = od
            target = (rx, ry)
    tr, tb = target

    myd = man(sx, sy, tr, tb)
    oppd = man(ox, oy, tr, tb)
    aim_collect = (oppd - myd) > 0  # we can reach first

    candidates = []
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = man(nx, ny, tr, tb)
        # scoring: primary reduce distance to target; secondary avoid worsening if contested
        dist_score = nd
        reach_gap = (oppd - nd)
        if aim_collect:
            # try to maximize gap (reach first), then reduce nd
            score = (0 if reach_gap > 0 else 1, -reach_gap, dist_score, (nx, ny))
        else:
            # intercept: minimize nd, then maximize reach_gap (reduce opponent advantage)
            score = (0, dist_score, -reach_gap, (nx, ny))
        candidates.append((score, [dx, dy]))

    # If all moves blocked, stay (engine will keep in place anyway)
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]