def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    res = [tuple(r) for r in resources]
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Precompute opponent distance to resources
    op_dists = []
    for rx, ry in res:
        op_dists.append(dist(ox, oy, rx, ry))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate by choosing the resource that maximizes our "will beat opponent" likelihood,
        # with small bias toward quick collection and toward denying closest resource paths.
        local_best = None
        local_block = None
        for i, (rx, ry) in enumerate(res):
            myd = dist(nx, ny, rx, ry)
            opd = op_dists[i]
            # If we can arrive strictly sooner, prioritize strongly; if tied/slower, de-prioritize.
            arrive_adv = opd - myd
            # Strong preference to any immediate pickup.
            immediate = 12 if (nx, ny) == (rx, ry) else 0
            val = immediate + (arrive_adv * 5) - (myd * 0.8) + ((opd - myd) > 0) * 2
            if local_best is None or (val, -myd, -rx, -ry, dx, dy) > local_best:
                local_best = (val, -myd, -rx, -ry, dx, dy)

            # Blocking term: if this move increases opponent's closest approach to resources they could take,
            # we get a slight bonus.
            # Approximate by how much closer opponent is after this move relative to our target distance.
            block_metric = opd - myd
            if local_block is None or (block_metric, -opd, -myd, -rx, -ry) > local_block:
                local_block = (block_metric, -opd, -myd, -rx, -ry)

        val_main = local_best[0]
        # Additional deterministic tie-break: prefer moves that reduce our distance to our best target and
        # avoid giving opponent immediate access.
        _, neg_my_d, _, _, _, _ = local_best
        my_d_bias = neg_my_d  # already negative
        # Deny bias: if opponent is very close to any resource, prefer moves that are closer than them.
        deny = 0
        for i, (rx, ry) in enumerate(res):
            myd = dist(nx, ny, rx, ry)
            opd = op_dists[i]
            if opd <= 2 and myd < opd:
                deny = 2

        total = val_main + (my_d_bias * 0.05) + deny + (local_block[0] * 0.15)
        tie = (total, local_best[1], local_best[2], local_best[3], -dx, -dy)
        if best_val is None or tie > best_val:
            best_val = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]