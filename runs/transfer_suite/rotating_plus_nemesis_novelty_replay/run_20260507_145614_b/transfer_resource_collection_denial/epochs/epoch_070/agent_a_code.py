def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if any((sx, sy) == (r[0], r[1]) for r in resources):
        return [0, 0]

    best = (0, 0)
    bestv = -10**18

    # New behavior: resource denial / contest. Prefer moves that reduce opponent advantage
    # on resources the opponent is currently closer to.
    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            nx, ny = sx, sy
            dxi, dyi = 0, 0

        my_focus = 0
        deny_focus = -10**18
        closest_my = 10**18
        closest_opp = 10**18

        for r in resources:
            rx, ry = r[0], r[1]
            myd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)

            if myd < closest_my:
                closest_my = myd
            if od < closest_opp:
                closest_opp = od

            # Contest weight: if opponent is closer, prioritize reducing that gap.
            gap = od - myd  # higher => we are closer
            if od < myd:
                # Strongly favor closing the gap quickly.
                val = (od - myd) / (myd + 1)
                if val > deny_focus:
                    deny_focus = val
            else:
                # Mildly reward resources we can likely secure.
                if gap > my_focus:
                    my_focus = gap

        # Decision combines: (1) denial if needed, else (2) secure/approach.
        # Anti-loop tie-break favors moving closer to some resource.
        if deny_focus > -10**17:
            v = 1000 * deny_focus + 3 * (-closest_my) + 0.1 * my_focus
        else:
            v = 10 * my_focus + (-closest_my) + 0.05 * (closest_opp - closest_my)

        if v > bestv:
            bestv = v
            best = (dxi, dyi)

    return [best[0], best[1]]