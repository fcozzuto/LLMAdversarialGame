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

    if not resources:
        # Move to reduce distance to opponent if no resources.
        best = (0, 0)
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -dist2(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Greedy contest metric: from candidate position, pick best resource by (opp_dist - self_dist) with tie-break.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Prefer staying flexible: light penalty for leaving board distance to center is not meaningful; use only local.
        cand = -10**18
        for rx, ry in resources:
            ds = dist2(nx, ny, rx, ry)
            do = dist2(ox, oy, rx, ry)
            # Larger is better: how much closer we are than opponent (in squared distance).
            v = (do - ds)
            # Tie-break: closer directly to that resource.
            v += -ds / 10.0
            # Small bias to avoid chasing resources that are effectively equally near opponent.
            if do == ds:
                v -= 0.5
            if v > cand:
                cand = v
        # Additional deterministic safety: slightly avoid moving toward opponent if we're not winning a contested target.
        opp_d = dist2(nx, ny, ox, oy)
        vtotal = cand - (0.03 * opp_d)
        if vtotal > bestv:
            bestv = vtotal
            best = (dx, dy)

    return [int(best[0]), int(best[1])]