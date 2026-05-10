def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    res_set = set(resources)

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1, h - 1)
        best, bestm = -10**18, [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            s = -cheb(nx, ny, tx, ty) + 0.01 * cheb(nx, ny, ox, oy)
            if s > best:
                best, bestm = s, [dx, dy]
        return bestm

    best, bestm = -10**18, [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Immediate collection
        s = 0
        if (nx, ny) in res_set:
            s += 1000

        # Battle over resources: reward being at least as close as opponent; penalize being behind.
        # Also keep pressure near closest resources (smaller distances matter more).
        local = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive if we are closer this move
            # Encourage claiming ties/advantage, but prefer nearer contests.
            contest_weight = 1.0 / (1 + do)
            if adv >= 0:
                local += (200 * adv + 20) * contest_weight
            else:
                local += (10 * adv) * contest_weight  # negative
        s += local

        # Tie-break: slightly prefer moves that also improve relative positioning vs opponent
        s += 0.01 * (cheb(ox, oy, nx, ny) - cheb(ox, oy, sx, sy))

        if s > best:
            best, bestm = s, [dx, dy]
    return bestm