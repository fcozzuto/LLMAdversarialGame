def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    if not resources:
        return [0, 0]

    # Compute current opponent best attraction (defense mode fallback)
    opp_best = min(cheb(ox, oy, rx, ry) for rx, ry in resources)

    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # If we can "keep up" with at least one resource, go on offense; else defend.
        found_nonneg = False
        offense_score = 0
        defense_score = 0

        # Offensive: maximize how much closer we are than opponent, weighted by resource proximity to us.
        for i, (rx, ry) in enumerate(resources):
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer
            if adv >= 0:
                found_nonneg = True
                # Prefer closer resources when competing; also strongly reward large positive adv.
                offense_score += (adv * 10) + (6 - min(myd, 6))
            else:
                # Still allow slightly negative ones if they are near; keep pressure on alternatives.
                if myd <= 2:
                    offense_score += (adv * 2) + (4 - myd)

            # Defense: measure how quickly opponent could reach its currently best target
            # (i.e., minimize opponent's closest distance after we move).
            # (Using current opponent position; our move affects future, but this still regularizes)
            if i == 0:
                pass

        if found_nonneg:
            val = offense_score
        else:
            # Defense: minimize opponent's best reachable distance to resources, with mild self-development.
            # Also slightly prefer moving toward the "hottest" resource for opponent to disrupt it.
            opp_closest = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            # Try to increase our distance from opponent, but primarily push to reduce opp's closest.
            val = (-opp_closest * 12) + (cheb(nx, ny, ox, oy) * -1) + (cheb(nx, ny, ox, oy) * 0)

        # Tie-break deterministically: prefer staying only if equal; then prefer smaller distance to our best resource.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val and (dx, dy) == (0, 0) and best_move != (0, 0):
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]