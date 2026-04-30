def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    best = None
    best_key = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # Prefer resources where we can arrive no later than opponent.
        # Key sorts: (advantage, -my_dist_to_resource, myd-opd, coords)
        advantage = opd - myd
        key = (
            1 if myd <= opd else 0,   # prefer non-losing races
            advantage,               # bigger is better
            -myd,                    # closer to us is better
            myd - opd,               # ties favor earlier
            rx * 11 + ry
        )
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_to_t = dist(nx, ny, tx, ty)
        # Secondary: don't let opponent get much closer to the target than we do.
        opp_to_t = dist(ox, oy, tx, ty)
        my_to_any = None
        # Small deterministic tie-break: keep moving toward the closest remaining resource after this step.
        # (Cheaper than full search; only over up to 12 resources.)
        min_any = 10**9
        for rx, ry in resources:
            d = dist(nx, ny, rx, ry)
            if d < min_any:
                min_any = d
        my_to_any = min_any

        mkey = (0 if (my_to_t == 0) else 1, my_to_t, -(opp_to_t - my_to_t), my_to_any, dx * 3 + dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]