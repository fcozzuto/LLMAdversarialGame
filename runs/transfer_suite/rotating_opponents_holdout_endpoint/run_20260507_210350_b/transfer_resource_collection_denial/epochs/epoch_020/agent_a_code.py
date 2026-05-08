def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    rset = set(resources)

    # Take a resource immediately if possible.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in rset:
            return [dx, dy]

    best_move = (0, 0)
    best_score = -10**18

    # Greedy: choose move that maximizes "lead" for the best obtainable resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = (nx, ny)

        # Evaluate the best target resource for this candidate.
        local_best = -10**18
        for tx, ty in rset:
            tr = (tx, ty)
            sd = dist(ns, tr)
            od = dist((ox, oy), tr)
            # Higher is better:
            # - large advantage (opponent further)
            # - closer to target (even if opponent also close)
            # - slight preference to reduce opponent's relative advantage.
            adv = od - sd
            score = 1000 * adv - sd
            if tr == (sx, sy):
                score += 2000
            if score > local_best:
                local_best = score

        # Break ties by preferring moving closer to the best local target direction.
        # (Deterministic: choose smaller dx, then smaller dy if score equal.)
        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)
        elif local_best == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]