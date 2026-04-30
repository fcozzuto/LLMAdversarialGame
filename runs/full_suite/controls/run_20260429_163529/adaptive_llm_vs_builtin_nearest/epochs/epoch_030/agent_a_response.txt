def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Choose target resource that I can reach sooner than opponent (or at least not much later).
    best_target = None
    best_val = -10**18
    for rx, ry in res:
        myd = cheb((sx, sy), (rx, ry))
        opd = cheb((ox, oy), (rx, ry))
        # Advantage: larger is better. Add a small preference for closer resources overall.
        val = (opd - myd) * 10 - myd
        # If opponent is extremely close, penalize more to avoid being scooped.
        if opd <= myd:
            val -= (myd - opd + 1) * 3
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    # If already on target, stay (or attempt to block by moving away from opponent's closest direction).
    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Greedy step towards target; if blocked, pick move minimizing distance to target while staying safe.
    best_move = None
    best_d = 10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = cheb((nx, ny), (tx, ty))
        # Avoid stepping into squares that make opponent closer to the same target than we remain.
        opd_next = cheb((ox, oy), (tx, ty))
        myd_next = d
        risk = 0
        if opd_next < myd_next:
            risk = (myd_next - opd_next + 1) * 2
        score = d + risk * 0.001  # mostly keep d, but break ties deterministically
        if score < best_d:
            best_d = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]