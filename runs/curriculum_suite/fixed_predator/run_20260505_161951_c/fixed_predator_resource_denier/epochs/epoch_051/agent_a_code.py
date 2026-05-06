def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            # Prefer opening space and drifting to the far corner of opponent pressure
            v = d_opp * 50 + (-(abs(nx - cx) + abs(ny - cy)))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a "contested" resource: prioritize ones opponent is closer to (denial value)
    # and ones we can move closer to (capture value).
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        # Center drift + obstacle avoidance already via valid().
        center_term = -(abs(nx - cx) + abs(ny - cy))

        movev = 0
        for rx, ry in resources:
            d_self_now = man(x, y, rx, ry)
            d_opp_now = man(ox, oy, rx, ry)
            d_self_next = man(nx, ny, rx, ry)
            d_opp_next = d_opp_now  # opponent move unknown; we use current distance as baseline contest.

            # Capture advantage grows when we move closer and opponent is not strictly closer.
            capture = (d_opp_now - d_self_next) * 20

            # Denial: resources opponent is already close to get high weight; we get extra credit if we reduce their lead.
            denial = (d_opp_now - d_self_now) * 8 + (d_opp_now - d_self_next) * 12

            # Immediate proximity bonus (likely to be taken next).
            prox = -cheb(nx, ny, rx, ry) * 6

            # If we are stepping onto/adjacent to a resource, boost strongly.
            on = 0
            if nx == rx and ny == ry:
                on = 200

            # Aggregate with a soft bias towards contested resources.
            contest = 1
            if d_opp_now <= d_self_now:
                contest = 2

            movev += contest * (capture + denial) + prox + on

        # Encourage not getting too close to opponent (prevents mirror traps) unless it helps capture.
        dist_opp = cheb(nx, ny, ox, oy)
        movev += dist_opp * 2

        movev += center_term
        if movev > bestv or (movev == bestv and (dx, dy) < best):
            bestv = movev
            best = (dx, dy)

    return [best[0], best[1]]