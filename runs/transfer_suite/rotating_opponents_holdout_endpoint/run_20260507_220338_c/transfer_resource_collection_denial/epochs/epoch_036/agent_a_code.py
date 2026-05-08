def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    res_list = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not res_list:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        local_best = -10**18
        for rx, ry in res_list:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Prefer resources we can reach first (or at least race competitively),
            # but also try to deny resources where opponent is currently favored.
            race = opd - myd  # positive is good for us
            gain = 12.0 * race
            proximity = -0.35 * myd
            deny = 0.0
            if race < 0 and opd <= 2:
                deny = 4.0 * (opd - myd)  # still negative but encourages closest interception
            pickup = 5.0 if myd == 0 else 0.0

            val = gain + proximity + deny + pickup
            if val > local_best:
                local_best = val

        # Light bias toward advancing generally (reduce deadlocks)
        advance = 0.08 * (abs(nx - (w - 1 - ox)) - abs(sx - (w - 1 - ox)))
        score = local_best + advance

        if score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]