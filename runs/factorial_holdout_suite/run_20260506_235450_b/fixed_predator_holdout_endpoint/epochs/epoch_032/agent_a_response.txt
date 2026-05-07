def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Late game: secure a pick. Early game: denial/contestation.
    late = int(observation.get("turns_remaining", 0) or 0) <= 4

    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate move by the best resource it can contest/secure next.
        if late:
            # Secure: maximize (self closeness), break ties by being farther from opponent (less contest pressure).
            best_for_move = -10**18
            for rx, ry in resources:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                val = (-sd * 10) + (od - sd)
                if val > best_for_move:
                    best_for_move = val
            val = best_for_move
        else:
            # Denial/contestation: prioritize resources where we are closer; if tied, go to the ones
            # where opponent is closer too (block them), and slightly favor nearer targets.
            val = -10**18
            for rx, ry in resources:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                swing = od - sd  # positive => we are winning the contest
                # Encourage stronger immediate swing and avoid very far targets.
                block = (1 if od <= sd + 1 else 0)
                cont = swing * 10 + block * 3 - sd
                if cont > val:
                    val = cont

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]