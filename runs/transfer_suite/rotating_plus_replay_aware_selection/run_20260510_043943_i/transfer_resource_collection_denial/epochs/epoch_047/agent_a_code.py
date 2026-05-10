def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds  # positive means we arrive earlier or same if ds<=do
            # prioritize guaranteed advantage, then minimize our distance, then deterministic cell preference
            v = adv * 10**6 - ds * 10**3
            if ds == 0:
                v += 10**10
            if adv < 0:
                v -= (abs(adv) * 10**5)  # strongly avoid targets we are late to
            v += -(rx * 13 + ry * 17) * 1e-6
            if v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best

    # One-step greedy with obstacle safety: choose move minimizing our distance to target,
    # but break ties by maximizing opponent being further from target.
    bestm = None
    bestmv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        ns = man(nx, ny, tx, ty)
        no = man(ox, oy, tx, ty)
        # prefer closer to target; if equal, prefer moves that don't worsen opponent contest (small bias)
        mv = -ns * 10**4 + (no - ns) * 1e-2 + -(nx * 7 + ny * 5) * 1e-6
        if bestm is None or mv > bestmv:
            bestm = (dx, dy)
            bestmv = mv

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]