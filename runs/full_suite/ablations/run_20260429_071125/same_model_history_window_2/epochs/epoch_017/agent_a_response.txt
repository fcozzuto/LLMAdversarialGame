def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            obstacles.add((p[0], p[1]))

    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_res(rx, ry):
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can match/beat soon; otherwise still move to something good.
        advantage = opd - myd
        # Deterministic tie-break by coordinates.
        return (-(advantage), myd, opd, rx, ry)

    targets = []
    for r in resources:
        if not r or len(r) != 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if inside(rx, ry):
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            targets.append((score_res(rx, ry), myd, opd, rx, ry))

    if targets:
        targets.sort(key=lambda t: t[0])
        tx, ty = targets[0][3], targets[0][4]
    else:
        tx, ty = sx, sy

    # Greedy move toward chosen target with obstacle avoidance; secondarily, avoid letting opponent improve.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd_next = cheb(nx, ny, tx, ty)
        # Predict whether this also helps us keep distance advantage over opponent to target.
        opd_next = cheb(ox, oy, tx, ty)
        my_adv = opd_next - myd_next
        # Deterministic: prefer maximizing my_adv, then smaller myd_next, then fixed move ordering.
        val = (-my_adv, myd_next, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]