def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    if resources:
        bestv = -10**18
        for tx, ty in resources:
            ds = md(sx, sy, tx, ty)
            do = md(ox, oy, tx, ty)
            # Prefer targets we're closer to, but also prefer still "high value" (tie-breaker by closeness).
            v = (do - ds) * 10 - ds
            if v > bestv:
                bestv = v
                target = (tx, ty)

    if target is None:
        # No resources visible: move toward opponent to reduce their options, otherwise stay safe.
        aim = (ox, oy)
    else:
        aim = target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds = md(nx, ny, aim[0], aim[1])
        do = md(ox + (1 if dx > 0 else -1 if dx < 0 else 0), oy + (1 if dy > 0 else -1 if dy < 0 else 0), aim[0], aim[1])
        # If a resource is at our next cell, heavily prefer it.
        got = 1 if target and (nx, ny) == target else 0
        # Avoid stepping adjacent to opponent if we're not securing immediately.
        adj = 1 if md(nx, ny, ox, oy) <= 1 else 0
        score = got * 10**6 - ds * 20 + (do - ds) * 3 - adj * 50
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]