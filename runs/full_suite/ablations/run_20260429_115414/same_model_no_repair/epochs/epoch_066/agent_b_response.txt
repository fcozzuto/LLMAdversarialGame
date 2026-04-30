def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Targeting: if resources exist, aim for the one where we can get and also where we can deny.
    # Otherwise, drift toward center while staying safe.
    target = None
    if resources:
        best_score = -10**18
        for rx, ry in resources:
            our_d = cheb(sx, sy, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources we are closer to; tie-break by overall closeness to us.
            sc = (opp_d - our_d) * 1000 - our_d * 10
            if sc > best_score:
                best_score = sc
                target = (rx, ry)

    if target is None:
        target = (w // 2, h // 2)

    best_move = [0, 0]
    best_val = -10**18

    # Deterministic tie-break: first best by value, then lexicographic dx,dy.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue

        val = 0
        # Core: contest resources
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            lead = opp_d - our_d
            # Strong reward if we reach the resource immediately or are already at it.
            if our_d == 0:
                val += 100000000
                continue
            # Being ahead is good; being behind is bad.
            if lead > 0:
                val += 2500 * lead // (1 + our_d)
            else:
                val -= 900 * (-lead) // (1 + our_d)
            # Also keep moving toward good targets we can influence.
            val += 40 * (cheb(nx, ny, rx, ry) * -1)

        # Safety/positioning: avoid moving away from the main target too much
        val += 60 * (cheb(sx, sy, target[0], target[1]) - cheb(nx, ny, target[0], target[1]))

        # Small preference to reduce distance to opponent (denial pressure) when it doesn't harm contesting
        val += 5 * (cheb(nx, ny, ox, oy) * -1)

        # Tie-break deterministically
        cand = (val, dx, dy)
        best = (best_val, best_move[0], best_move[1])
        if cand > best:
            best_val = val
            best_move = [dx, dy]

    return best_move