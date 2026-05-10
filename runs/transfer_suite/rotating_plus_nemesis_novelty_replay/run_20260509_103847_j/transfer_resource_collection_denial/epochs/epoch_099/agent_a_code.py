def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target a resource where we can be (or become) closer than opponent.
    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate move by best resource we could claim first.
        move_best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_me = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)

            # Prefer resources we are closer to (or tie), with a secondary bias:
            # if denier blocks from the right side, contest by moving toward resources
            # nearer to opponent along x-direction.
            closer_margin = d_op - d_me
            tie_row = 1 if (rx == ox) else 0  # opponent alignment in x tends to correlate with denials
            # Lexicographic: maximize margin, then minimize our distance, then maximize alignment, then minimize opp distance.
            key = (closer_margin, -d_me, tie_row, -d_op)
            if move_best_key is None or key > move_best_key:
                move_best_key = key

        if move_best_key is None:
            continue

        # Slight preference to avoid dithering: prefer actions that reduce our distance to the overall best target.
        # Deterministic: break ties by dx,dy ordering via tuple.
        if best_key is None or move_best_key > best_key:
            best_key = move_best_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]