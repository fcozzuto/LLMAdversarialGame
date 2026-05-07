def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Opponent's nearest reachable resource (for mild blocking pressure)
    opp_near = None
    opp_min = 10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = man(ox, oy, rx, ry)
        if d < opp_min:
            opp_min = d
            opp_near = (rx, ry)

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0.0
        # Favor moves that let us arrive no later than the opponent on more/better resources.
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds <= do:
                score += 2.0 / (ds + 1)  # earlier access matters
            else:
                # discourage committing to resources opponent gets first
                score -= 1.0 / (ds + 1) - 0.2 / (do + 1)

        # Additional deterministic pressure: increase distance of opponent from its nearest target.
        if opp_near is not None:
            trx, try_ = opp_near
            base = man(ox, oy, trx, try_)
            # approximate effect: moving ourselves shouldn't change opponent distance, but
            # we can still prefer lines that reduce our future interception risk.
            # Use a proxy: closer to that target from our next position is better.
            score += 0.5 / (man(nx, ny, trx, try_) + 1)
            score -= 0.01 * (base)  # negligible bias to keep behavior stable

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]