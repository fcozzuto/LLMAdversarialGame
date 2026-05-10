def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    turns_remaining = observation.get("turns_remaining", 0)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        for r in resources:
            if r[0] == sx and r[1] == sy:
                return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Late game: be greedy for immediate pickups; early: deny by choosing resources we reach sooner.
    late = 1.0 if turns_remaining <= 10 else 0.0
    reach_weight = 1.0 + 2.0 * (1.0 - late)  # more important early
    opp_weight = 1.5 + 1.5 * (1.0 - late)   # more important early

    best = (-10**18, 0, 0)
    # If no resources, move toward opponent opposite corner-ish (deterministic).
    if not resources:
        tx = w - 1 if sx < w - 1 else 0
        ty = h - 1 if sy < h - 1 else 0
        bestd = 10**9
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) < bestm):
                bestd = d
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose best target resource from this move.
        best_target = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach first; also prefer closer ones.
            # Penalize if opponent can reach much earlier (resource denial threat).
            urgency = 20.0 / (1.0 + myd)
            lead = (opd - myd)
            deny = (lead >= 0) * (5.0 + 0.5 * lead) - (lead < 0) * (6.0 + 1.0 * (-lead))
            target_score = reach_weight * (-myd) + opp_weight * deny + (late * urgency) + ((1.0 - late) * (1.0 if lead >= 0 else 0.0))
            if target_score > best_target:
                best_target = target_score

        # Add slight preference for reducing distance to current best target versus staying.
        total = best_target
        if total > best[0] or (total == best[0] and (dx, dy) < (best[1], best[2])):
            best = (total, dx, dy)

    return [best[1], best[2]]