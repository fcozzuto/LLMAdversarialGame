def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def next_pos(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            return x, y
        return nx, ny

    # If capture is possible immediately, do it (capture_radius == 0)
    for dx, dy in moves:
        nx, ny = next_pos(sx, sy, dx, dy)
        if nx == ox and ny == oy:
            return [dx, dy]

    # One-step minimax: if we're pursuer -> minimize distance under opponent maximizing response.
    # If we're evader -> maximize our survival distance under pursuer maximizing capture pressure (approx).
    best_move = [0, 0]
    best_val = None

    for my_dx, my_dy in moves:
        nx, ny = next_pos(sx, sy, my_dx, my_dy)

        worst_or_best = None
        for ex_dx, ex_dy in moves:
            ex, ey = next_pos(ox, oy, ex_dx, ex_dy)

            if ex == nx and ey == ny:
                # capture state: pursuer wants it; evader wants to avoid it
                val = -10**9 if not evader else 10**9
            else:
                val = dist2(nx, ny, ex, ey)

            # pursuer (evader==False): opponent picks max distance; we pick min worst-case
            # evader (evader==True): opponent (pursuer) picks min distance to us; we pick max best-case
            if worst_or_best is None:
                worst_or_best = val
            else:
                if evader:
                    # opponent response minimizes our distance -> smaller dist2 is worse for us
                    worst_or_best = min(worst_or_best, val)
                else:
                    # opponent response maximizes distance -> larger dist2 is better for opponent
                    worst_or_best = max(worst_or_best, val)

        if best_val is None:
            best_val = worst_or_best
            best_move = [my_dx, my_dy]
        else:
            if evader:
                # choose move that maximizes the best-case (largest worst_or_best)
                if worst_or_best > best_val:
                    best_val = worst_or_best
                    best_move = [my_dx, my_dy]
            else:
                # choose move that minimizes the worst-case (smallest worst_or_best)
                if worst_or_best < best_val:
                    best_val = worst_or_best
                    best_move = [my_dx, my_dy]

    return best_move