def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If no visible resources, keep distance while drifting toward center.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best, bestv = (0, 0), None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            tv = (man(nx, ny, ox, oy), -abs(nx - cx) - abs(ny - cy), -abs(dx) - abs(dy))
            if bestv is None or tv > bestv:
                bestv, best = tv, (dx, dy)
        return [best[0], best[1]]

    # Prefer resources where we are closer than the opponent, otherwise use best tradeoff.
    best, bestv = (0, 0), None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        oppd = man(nx, ny, ox, oy)
        # Primary: maximize (opp_dist - my_dist) across resources, with tie-breaker on my distance.
        best_resource_score = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Positive favors grabbing where opponent is farther.
            rs = (od - sd, -sd, -man(nx, ny, ox, oy))
            if best_resource_score is None or rs > best_resource_score:
                best_resource_score = rs
        # Secondary: keep some spacing from opponent to reduce direct contest losses.
        tv = (best_resource_score[0], best_resource_score[1], oppd, -abs(dx) - abs(dy), dx, dy)
        if bestv is None or tv > bestv:
            bestv, best = tv, (dx, dy)

    return [best[0], best[1]]