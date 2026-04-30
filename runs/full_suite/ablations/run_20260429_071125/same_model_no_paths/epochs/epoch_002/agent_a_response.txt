def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    opp = (ox, oy)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        selfp = (nx, ny)

        # Evaluate best contest we create next move.
        # advantage > 0 means we are closer (by manhattan) than opponent.
        best_adv = -10**9
        best_dist = 10**9
        best_opp = 10**9
        for r in resources:
            rd = (r[0], r[1])
            our_d = man(selfp, rd)
            opp_d = man(opp, rd)
            adv = opp_d - our_d
            # Prefer creating/maintaining positive advantage; otherwise reduce opponent advantage.
            if adv > best_adv or (adv == best_adv and our_d < best_dist):
                best_adv = adv
                best_dist = our_d
                best_opp = opp_d

        # Extra pressure to move toward resources near the opponent (contesting/stealing).
        # Scale with how many resources remain.
        remaining = observation.get("remaining_resource_count", len(resources))
        pressure = (12 - remaining) / 12.0 if remaining is not None else 0.0
        score = best_adv * 1000 + (best_opp - best_dist) * 25 + (-best_dist) * (1.0 + pressure)

        # Deterministic tie-breaks: prefer smaller distance to best target, then lexicographic move.
        key = (score, -best_adv, -best_opp, -best_dist, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]