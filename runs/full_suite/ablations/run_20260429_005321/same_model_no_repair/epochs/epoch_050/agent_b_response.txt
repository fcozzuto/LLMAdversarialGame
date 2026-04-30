def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation["grid_width"]
    gh = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate move by its best attainable "beat opponent" advantage.
        val = -10**18
        for rx, ry in resources:
            sd = king_dist(nx, ny, rx, ry)
            od = king_dist(ox, oy, rx, ry)
            # Positive when we are closer to this resource than opponent.
            adv = od - sd
            # Strongly prefer immediate winning races, then reduce our distance.
            v = adv * 140 - sd * 6
            # If we would still be behind, avoid it unless it denies a very near opponent win.
            if adv < 0:
                v -= (-adv) * 40
            if v > val:
                val = v

        # If we can't reach any resources efficiently, at least minimize our distance to the nearest resource.
        if val == -10**18:
            val = -min(king_dist(nx, ny, rx, ry) for rx, ry in resources)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]