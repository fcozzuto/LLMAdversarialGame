def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = None
        bestm = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = man(nx, ny, ox, oy)
            if best is None or val < best:
                best = val
                bestm = [dx, dy]
        return bestm

    best_val = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Pick the resource where we gain most over the opponent.
        best_for_move = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer than opponent
            # Also penalize letting opponent be strictly closer (negative adv).
            val = (adv, -ds, -man(nx, ny, ox, oy))
            if best_for_move is None or val > best_for_move:
                best_for_move = val

        # If multiple resources yield same best_for_move, prefer keeping distance to opponent moderate.
        # best_for_move already includes -distance-to-opp term, so just compare tuples.
        if best_val is None or best_for_move > best_val:
            best_val = best_for_move
            best_move = [dx, dy]

    return best_move