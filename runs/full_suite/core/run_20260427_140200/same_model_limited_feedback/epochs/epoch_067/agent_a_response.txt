def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((x, y) for x, y in obstacles)
    opp = (ox, oy)
    if not resources:
        # Simple fallback: move toward center
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference: closer to resources, then away from immediate opponent proximity
    best = None
    best_h = 10**9

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        # Evaluate contest over resources
        self_pos = (nx, ny)
        opp_dist_pen = 0
        d_opp = dist2(self_pos, opp)
        if d_opp <= 2:  # adjacent-ish (includes diagonal/orthogonal)
            opp_dist_pen = 6

        # Compute best (smallest) "advantage" metric among resources
        # advantage = dist_self - 0.85*dist_opp, so lower favors where we are relatively closer
        best_adv = 10**18
        for rx, ry in resources:
            rpos = (rx, ry)
            adv = dist2(self_pos, rpos) - 0.85 * dist2(opp, rpos)
            if adv < best_adv:
                best_adv = adv

        # Additional bias: prefer reducing our distance to the nearest resource
        nearest = 10**18
        for rx, ry in resources:
            nearest = min(nearest, dist2(self_pos, (rx, ry)))

        h = best_adv + 0.15 * nearest + opp_dist_pen
        if h < best_h:
            best_h = h
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best