def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def blocked(x, y):
        return (x, y) in obstacles or not in_bounds(x, y)

    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        best_v = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            v = -md(nx, ny, tx, ty)
            if v > best_v:
                best_v = v
                best = [dx, dy]
        return best

    # Greedy with denial-aware scoring and one-step lookahead.
    # Score favors: being closer to a resource than opponent, and avoiding giving up nearest resources.
    best_move = [0, 0]
    best_score = -10**18
    k_den = 3.0  # denial emphasis
    k_margin = 1.0  # reward closeness advantage
    k_fallback = 0.2  # small preference for nearer overall

    # Precompute top resources to stabilize determinism under ties
    res_sorted = sorted(resources, key=lambda r: (r[0], r[1]))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        move_score = -md(nx, ny, ox, oy) * 0.05  # slight separation to avoid collision patterns

        # Evaluate resources after the move
        for i, (rx, ry) in enumerate(res_sorted):
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)

            # If we can reach immediately, big win signal
            if ds == 0:
                s = 1000.0
            else:
                # margin positive means we are closer than opponent
                margin = (do - ds)
                # favor nearer and clearer margins; penalize giving opponent a huge head start
                s = k_margin * margin - k_den * max(0, -margin) - k_fallback * ds

                # small tie-breaker favor higher "reach order" by grid position deterministically
                s -= 0.001 * i

            # If opponent is currently adjacent, prefer resources we can secure over contesting
            if md(ox, oy, rx, ry) == 1 and ds > 0:
                s -= 5.0

            # If our move makes us relatively the best contender for this resource, emphasize
            s += 0.01 * (md(sx, sy, rx, ry) - ds)

            move_score = max(move_score, s)

        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]

    return best_move