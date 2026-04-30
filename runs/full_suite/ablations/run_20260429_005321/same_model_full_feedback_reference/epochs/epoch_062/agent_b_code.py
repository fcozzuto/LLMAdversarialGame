def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If no resources: advance toward opponent while respecting obstacles.
    if not resources:
        best = (0, 0)
        bestv = -10**30
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # With resources: pick move maximizing (closer to a target resource) and (farther from opponent on it).
    best = (0, 0)
    bestv = -10**30
    alpha = 0.75  # oppose opponent's access
    beta = 0.08   # slightly avoid getting too close to opponent

    # deterministic target ordering
    resources.sort(key=lambda t: (t[0], t[1]))
    target_pick_limit = 6

    cand_resources = resources[:target_pick_limit]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # prefer reducing our distance to best reachable target, while keeping opponent away
        v = 0
        # compute best target utility for this move
        mv_best = -10**30
        for tx, ty in cand_resources:
            d_me = dist2(nx, ny, tx, ty)
            d_op = dist2(ox, oy, tx, ty)
            # closer is better for us: smaller d_me; farther is better vs opponent: larger d_op
            util = (-d_me) + alpha * d_op
            # small tie-breaker: avoid paths that are too close to opponent
            util -= beta * dist2(nx, ny, ox, oy)
            if util > mv_best:
                mv_best = util
        # if opponent is adjacent, bias toward resources that are also near us (more urgent)
        if dist2(sx, sy, ox, oy) <= 2:
            urgency = -min(dist2(nx, ny, tx, ty) for tx, ty in cand_resources)
            v = mv_best + 0.15 * urgency
        else:
            v = mv_best
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]