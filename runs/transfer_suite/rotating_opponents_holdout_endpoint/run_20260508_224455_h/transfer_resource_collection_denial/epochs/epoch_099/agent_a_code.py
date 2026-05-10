def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx + dy

    res = []
    for r in resources:
        x, y = int(r[0]), int(r[1])
        if inb(x, y) and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    # Candidate resources: prefer ones in rows/cols that reduce our lead; deterministic shortlist
    res.sort(key=lambda p: (dist((sx, sy), p) - dist((ox, oy), p), dist((ox, oy), p), p[0], p[1]))
    res = res[:10]

    def cell_adv(myx, myy, rx, ry):
        # Higher is better: get lead on opponent; small preference for nearer resource
        ds = dist((myx, myy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        return (do - ds) * 10 - ds

    best = (-(10**18), 0, 0)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # If we can step onto a resource, heavily prioritize it
        step_bonus = 0
        # Deterministic membership check by scanning small list
        for r in res:
            if r[0] == nx and r[1] == ny:
                step_bonus = 1000000
                break
        best_cell = -(10**18)
        for rx, ry in res:
            v = cell_adv(nx, ny, rx, ry)
            # If opponent is very close, discourage
            if dist((ox, oy), (rx, ry)) <= 1 and dist((nx, ny), (rx, ry)) > 1:
                v -= 5000
            if v > best_cell:
                best_cell = v
        v = best_cell + step_bonus
        # tie-break deterministically by move order
        if (v, dxm, dym) > best:
            best = (v, dxm, dym)

    return [int(best[1]), int(best[2])]