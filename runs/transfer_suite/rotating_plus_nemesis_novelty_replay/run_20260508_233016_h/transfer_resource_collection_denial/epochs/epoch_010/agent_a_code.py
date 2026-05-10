def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a deterministic best resource to pursue:
    # Prefer resources where we are closer than opponent by the biggest margin.
    best_r = None
    best_margin = None
    best_opp = None
    for r in resources:
        rx, ry = r
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        margin = od - sd  # positive => we are closer
        if best_margin is None or margin > best_margin or (margin == best_margin and (best_opp is None or od < best_opp)):
            best_margin = margin
            best_opp = od
            best_r = (rx, ry)

    # If we are not ahead on any resource, contest the most urgent one (smallest opponent distance).
    if best_margin is None or best_margin <= 0:
        best_r = None
        best_opp = None
        for r in resources:
            rx, ry = r
            od = dist(ox, oy, rx, ry)
            if best_opp is None or od < best_opp or (od == best_opp and dist(sx, sy, rx, ry) < dist(sx, sy, best_r[0], best_r[1])):
                best_opp = od
                best_r = (rx, ry)

    rx, ry = best_r

    # Evaluate move: reduce our distance to target, and (secondary) avoid giving opponent easy access.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_d = dist(nx, ny, rx, ry)
        # Opponent potential: how close opponent is to our target after we move (assume they continue their nearest-resource).
        opp_d = dist(ox, oy, rx, ry)

        # Small bias to move toward resources generally if target distance ties.
        nearest_resource_d = None
        for r2 in resources:
            rx2, ry2 = r2
            d2 = dist(nx, ny, rx2, ry2)
            if nearest_resource_d is None or d2 < nearest_resource_d:
                nearest_resource_d = d2

        # Deterministic tie-break: prefer lower dx, then lower dy.
        score = (my_d, -opp_d, nearest_resource_d, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move