def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick best resource targets to race: prefer those where we are not slower.
    best = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = (do - ds)
        if ds <= do:
            pr = 2
        else:
            pr = 1
        best.append((pr, lead, -do, -ds, rx, ry, ds, do))
    best.sort(reverse=True)
    top = best[: min(6, len(best))]

    # Candidate moves scored by resulting distance to best target set.
    best_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            move_score = 0
            # If we step onto a resource, heavily prefer it.
            if (nx, ny) in set(tuple(r) for r in resources):
                move_score += 1_000_000

            # Evaluate against top targets: reward reducing our distance, especially when we're not slower than opponent.
            for pr, lead, n_do, n_ds, rx, ry, ds, do in top:
                ds2 = cheb(nx, ny, rx, ry)
                do2 = cheb(ox, oy, rx, ry)  # opponent assumed stationary for 1-step look
                if ds2 <= do2:
                    move_score += 3000 + (do2 - ds2) * 50
                else:
                    move_score += (do2 - ds2) * 5  # still small pressure to get closer

                # Additional reward for dropping our absolute distance.
                move_score += (ds - ds2) * 20

            # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying.
            best_moves.append((move_score, -abs(dx) - abs(dy), -dx, -dy, dx, dy))

    best_moves.sort(reverse=True)
    return [int(best_moves[0][4]), int(best_moves[0][5])]