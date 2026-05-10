def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obs = set((x, y) for x, y in obstacles)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    tr = int(observation.get("turns_remaining", 0))
    best_key = None
    best = resources[0]

    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)

        # Primary: only commit to resources we can reach no later than opponent.
        # Secondary: otherwise contest the earliest resource opponent is likely to take.
        if myd <= opd:
            # Prefer smaller myd, and also smaller (opponent lead) to keep contest tight.
            key = (0, -(opd - myd), -myd, rx * 100 + ry)
        else:
            # Contest score: negative means "bad" (opponent leads), so try to maximize opponent urgency.
            # If we can't reasonably arrive before game ends, heavily penalize.
            late = 0 if myd <= tr else (myd - tr)
            key = (1, late * 100 + (opd - myd), myd, -(opd), rx * 100 + ry)

        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Attempt direct step; if blocked, try axis alternatives deterministically.
    candidates = [(dx, dy), (dx, 0), (0, dy), (-dx, 0), (0, -dy), (0, 0)]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if (nx, ny) not in obs:
            return [int(mx), int(my)]
    return [0, 0]