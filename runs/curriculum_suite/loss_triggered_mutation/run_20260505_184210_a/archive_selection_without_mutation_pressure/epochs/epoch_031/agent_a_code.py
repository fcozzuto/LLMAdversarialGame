def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Simple guard: move to increase distance from opponent while staying mobile.
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Predict opponent's next target as its nearest resource (chebyshev).
    target = min(resources, key=lambda r: cheb(ox, oy, r[0], r[1]))
    tx, ty = target[0], target[1]
    opp_to_target = cheb(ox, oy, tx, ty)

    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        self_to_target = cheb(nx, ny, tx, ty)

        # Intercept objective around the predicted target.
        lead = opp_to_target - self_to_target  # positive means we are closer than opponent.
        # Approximate that opponent can reduce its distance by 1 per move.
        lead_next = (opp_to_target - 1) - self_to_target

        # If behind on target, also bias toward making it harder by increasing distance from opponent.
        dist_opp = cheb(nx, ny, ox, oy)
        v = 0.0
        v += 3.0 * lead_next
        v += 0.2 * lead
        v += -0.05 * self_to_target
        if lead_next < 0:
            v += 0.08 * dist_opp

        # If we can secure the predicted target soon, consider switching to the best alternative.
        if lead_next >= 0:
            # Find best alternative relative advantage at this move.
            alt_best = -10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                alt_best = max(alt_best, (od - sd) - 0.03 * sd)
            v += 0.35 * alt_best

        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]