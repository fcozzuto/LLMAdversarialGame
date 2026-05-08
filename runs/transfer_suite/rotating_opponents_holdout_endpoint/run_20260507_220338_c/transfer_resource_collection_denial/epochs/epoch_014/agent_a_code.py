def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Deterministic tie-break: fixed ordering, and add tiny epsilon based on index.
    best_score = -10**30
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_score = -10**30
        # Evaluate best target resource we could collect sooner than opponent.
        for i, (rx, ry) in enumerate(resources):
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)

            if nx == rx and ny == ry:
                # Direct collection dominates.
                s = 10**9 - i
            else:
                # Race advantage: prefer resources we reach no later than opponent, and closer.
                # If opponent is already closer, we still may go for it but strongly prefer where we lead.
                lead = od - sd
                s = lead * 2000 - sd * 10 - i
                if lead < 0:
                    s -= (-lead) * 50

            # Small deterministic bias toward moves that reduce our distance to opponent
            # only when breaking ties on resource desirability.
            if s > move_score:
                move_score = s

        # Secondary criterion: keep pressure by also reducing our distance to the opponent when tied.
        opp_pressure = -(md(nx, ny, ox, oy))
        final_score = move_score * 1000 + opp_pressure

        if final_score > best_score:
            best_score = final_score
            best_move = [dx, dy]

    # If somehow no legal move, stay.
    return best_move if best_move is not None else [0, 0]