def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Target resources: prioritize getting there at least 1 step earlier than opponent (avoid contested grabs)
        best_adv = -10**18
        best_fallback = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive is our lead
            # Lead score: strongly prefer clearing lead by >=1, and closer resources
            lead_score = 120 * adv - 2.0 * ds
            # Fallback: if no lead, prefer resources opponent is far from (less likely to steal)
            fallback_score = 80 * (do - ds if do - ds > 0 else 0) + 0.5 * do - 1.0 * ds

            if lead_score > best_adv:
                best_adv = lead_score
            if fallback_score > best_fallback:
                best_fallback = fallback_score

        score = best_adv
        if best_adv < 0:
            # No winning lead exists from this move: switch to safer anti-steal fallback and keep distance from opponent.
            score = best_fallback + 0.3 * cheb(nx, ny, ox, oy)

        # Small preference for progressing: reduce distance to the closest resource (deterministic tiebreaker)
        score -= 0.01 * min(cheb(nx, ny, rx, ry) for rx, ry in resources)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]