def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_list = [tuple(r) for r in resources]
    best_moves = []
    best_val = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx; ny = sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue

            # Evaluate this move by the best "swing" we can create on any resource.
            # Swing: opponent-distance minus our-distance (positive means we can arrive first).
            # Add tie-break: prefer resources that are not "contested tightly" and not too far.
            move_best = -10**18
            for rx, ry in res_list:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                swing = do - ds
                # Strongly reward high swing; modestly prefer shorter routes.
                val = swing * 10000 - ds * 30 - (rx + ry) * 0.01
                # If opponent is already adjacent/near, slightly bias away to avoid denial races.
                if do <= 1 and swing <= 1:
                    val -= 5000
                if val > move_best:
                    move_best = val

            if move_best > best_val:
                best_val = move_best
                best_moves = [(dx, dy)]
            elif move_best == best_val:
                best_moves.append((dx, dy))

    # Deterministic tie-break: smallest lexicographic (dx, dy).
    best_moves.sort()
    return [best_moves[0][0], best_moves[0][1]]