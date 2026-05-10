def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Prefer contesting opponent's current "sweep" line (row) while still collecting.
    def target_value(px, py, rx, ry):
        ds = abs(rx - px) + abs(ry - py)
        do = abs(rx - ox) + abs(ry - oy)
        # Higher is better: we become relatively closer; tie-break favors being on their row.
        adv = do - ds
        row_contest = 2 if ry == oy else 0
        # If near, slightly prioritize quick completion.
        near = 0.15 if ds <= 1 else 0.0
        return (adv + row_contest + near, -ds)

    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        # Choose best resource for this move, then estimate how competitive it is.
        best = None
        for rx, ry in resources:
            tv = target_value(nx, ny, rx, ry)
            if best is None or tv > best:
                best = tv
        # Encourage staying safe from being too far when opponent is near a resource.
        # Also discourage moving away from the best target we found.
        return best[0] + best[1]

    bestm = None
    bests = -10**18
    # Deterministic tie-break order
    for dx, dy in deltas:
        sc = move_score(dx, dy)
        if sc > bests:
            bests = sc
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]