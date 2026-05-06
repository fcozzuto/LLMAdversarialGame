def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dsq(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if not resources:
        # Deterministic: move to keep distance from opponent (shadow separation).
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            val = -dsq(nx, ny, ox, oy)
            key = (val, nx, ny)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # Contest logic: prefer a resource that the opponent is currently closer to.
    my_best = min(resources, key=lambda r: dsq(sx, sy, r[0], r[1]))
    contest = []
    for r in resources:
        dm = dsq(sx, sy, r[0], r[1])
        do = dsq(ox, oy, r[0], r[1])
        if do < dm:  # opponent has advantage here; attempt to intercept
            contest.append((r, do - dm, do))
    target = None
    if contest:
        # Pick most "overlapping" advantage first (opponent much closer), then nearest to opponent.
        contest.sort(key=lambda t: (-t[1], t[2], t[0][0], t[0][1]))
        target = contest[0][0]
    else:
        target = my_best

    tx, ty = target
    # Move choice: minimize my distance to target, but also slightly reduce opponent-target gap.
    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        myd = dsq(nx, ny, tx, ty)
        opd = dsq(ox, oy, tx, ty)
        opp_gap = myd - opd
        # Primary: myd; Secondary: reduce opponent advantage (make opp_gap smaller); Tertiary deterministic coords.
        key = (myd, opp_gap, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move