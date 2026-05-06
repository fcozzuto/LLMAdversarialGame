def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18
    best_t = 10**18  # tie-break: prefer smaller distance to chosen target
    best_sep = -10**18  # tie-break: prefer keeping distance from opponent

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Pick the resource that maximizes our lead after this move.
        # Lead = opponent_cheb_dist - our_cheb_dist (bigger is better).
        lead_best = -10**18
        t_best = 10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lead = opd - myd
            # small tie-break: prefer closer target if lead equal
            if lead > lead_best or (lead == lead_best and myd < t_best):
                lead_best = lead
                t_best = myd

        # If we can't get a positive lead, still move toward the best attainable lead.
        sep = cheb(nx, ny, ox, oy)
        # Main score: lead, plus slight bias to reduce our distance to that best target.
        score = lead_best * 1000 - t_best + sep * 0.01

        # Deterministic tie-breakers:
        # 1) higher score
        # 2) smaller distance to target
        # 3) larger separation from opponent
        # 4) prefer non-stay if tied
        if score > best_score or (score == best_score and (t_best < best_t or (t_best == best_t and (sep > best_sep or (sep == best_sep and (dx, dy) != (0, 0)))))):
            best_score = score
            best_t = t_best
            best_sep = sep
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]