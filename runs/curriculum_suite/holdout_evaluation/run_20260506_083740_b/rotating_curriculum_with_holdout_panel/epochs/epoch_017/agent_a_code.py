def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_op = abs(nx - ox) + abs(ny - oy)
            v = -d_op
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-breaker by lexicographic move order.
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # "Shadow-block" objective: maximize our worst disadvantage across resources.
        worst_adv = 10**9
        for rx, ry in resources:
            ds = dist(nx, ny, sx, sy)  # unused but deterministic placeholder not allowed; remove
        worst_adv = 10**9
        for rx, ry in resources:
            ds = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)
            adv = ds - do  # lower is worse; we maximize (negative) => maximize adv is better
            if adv < worst_adv:
                worst_adv = adv
        # Convert "advantage being less negative" into higher-is-better score.
        # If opponent is much closer, worst_adv is negative; we still pick max to reduce negativity.
        d_op = abs(nx - ox) + abs(ny - oy)
        # Extra pressure to intercept when we're losing everywhere.
        # This discourages simply drifting toward far resources while opponent is nearer.
        # Since worst_adv is large/positive when we are behind less, intercept term is mild.
        intercept_weight = 1.0 + (0 if worst_adv >= 0 else min(4.0, -worst_adv * 0.5))
        val = (-worst_adv) * 10.0 - d_op * intercept_weight
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]