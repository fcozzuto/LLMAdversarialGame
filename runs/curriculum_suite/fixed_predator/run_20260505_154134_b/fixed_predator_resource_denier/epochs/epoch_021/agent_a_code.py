def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # For each move, score by best resource we can beat opponent on (plus pick-up proximity).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_to_opp = cheb(nx, ny, ox, oy)
        score = 0
        taken = False
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # If we can arrive not later than opponent, prioritize strongly; otherwise, still prefer stealing proximity.
            # Deterministic tie-break via (lexicographic) when equal at end.
            rel = do - ds  # positive means we are closer or equal
            val = (rel * 1000) - ds * 3 - my_to_opp * 0.1 - (rx + ry) * 0.001
            if not taken or val > score:
                score = val
                taken = True

        # If no valid resources, keep position-ish toward opponent.
        if not taken:
            score = -my_to_opp

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]