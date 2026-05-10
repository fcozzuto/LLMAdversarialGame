def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    best = None
    best_rank = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        adv = myd - opd  # negative is good (I closer)
        # Rank: prefer advantage, then faster for me, then farther from opponent
        rank = (0 if adv <= 0 else 1, adv, myd, -opd)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best = (rx, ry)

    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose step that most reduces my distance to target; if tie, step that keeps my advantage (or improves it)
    best_step = (0, 0)
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = man(nx, ny, tx, ty)
        # compute how my step changes advantage at the same target
        myd2 = d_to
        opd_same = man(ox, oy, tx, ty)
        adv2 = myd2 - opd_same
        s = (d_to, 0 if adv2 <= 0 else 1, abs(adv2), abs(nx - ox) + abs(ny - oy))
        if best_s is None or s < best_s:
            best_s = s
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]