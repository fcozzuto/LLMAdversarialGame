def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev on diagonals

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return [0 if sx == tx else (1 if tx > sx else -1), 0 if sy == ty else (1 if ty > sy else -1)]

    # If standing on a resource, collect.
    for rx, ry in resources:
        if (sx, sy) == (rx, ry):
            return [0, 0]

    # Strategy shift: prioritize resources where we can arrive sooner than opponent,
    # and if none, pick resource that minimizes our arrival time while also not
    # giving opponent an immediate fork (via negative advantage).
    best = (0, 0)
    best_val = -10**18
    best_my_d = 10**9
    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            nx, ny = sx, sy
            dxi, dyi = 0, 0

        my_best = 10**9
        opp_for_that = 10**9
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            if myd < my_best:
                my_best = myd
                opp_for_that = od

        # Advantage margin: positive means we are (likely) earlier from next position.
        adv = opp_for_that - my_best

        # Secondary pressure: avoid moves that make opponent too close to our next target.
        # Also prefer smaller my_best (faster collection).
        val = adv * 1000 - my_best * 3 - max(0, 10 - adv) * 7
        # Tie-break deterministically toward reducing distance to opponent-held pressure:
        if val > best_val or (val == best_val and (my_best < best_my_d or (my_best == best_my_d and (dxi, dyi) < best))):
            best_val = val
            best_my_d = my_best
            best = (dxi, dyi)

    return [int(best[0]), int(best[1])]