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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_target = min(resources, key=lambda r: cheb(ox, oy, r[0], r[1]))

    best = (0, 0)
    bestv = -10**18
    cur_t = cheb(sx, sy, opp_target[0], opp_target[1])

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary: maximize worst-case advantage to any resource (relative to opponent).
        worst = 10**18
        best_local = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            cur_my = cheb(sx, sy, rx, ry)

            # If opponent is at/near the resource, treat as very risky.
            if opd <= 1:
                adv = -1000 - myd
            else:
                # Higher when we are closer than opponent and when we make progress.
                adv = (opd - myd) * 30 + (cur_my - myd) * 6 - myd
            if adv < worst:
                worst = adv
            if adv > best_local:
                best_local = adv

        # Secondary tie-break: if opponent has a very close target, allow "interception" pressure.
        new_t = cheb(nx, ny, opp_target[0], opp_target[1])
        intercept = (cur_t - new_t) * 12 - new_t * 1

        # Combine: prioritize improving the worst resource opportunity; then best single opportunity.
        v = worst * 2 + best_local + intercept
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]