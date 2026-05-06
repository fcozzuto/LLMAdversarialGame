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

    if not resources:
        best = (0, 0)
        bestv = -10**18
        tx, ty = w - 1, h - 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            # keep moving away from being trapped symmetrically
            v = d_opp * 1000 - (abs(nx - tx) + abs(ny - ty))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Opportunistic switching: either take a resource we can beat, or deny one they are about to get.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        # If we land on a resource, that's best.
        if (nx, ny) in obs:
            continue
        best_cell = -10**18
        for rx, ry in resources:
            us_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - us_d  # positive means we are closer (good vs denier)
            # prefer near-term wins; if we can't win, move to resources where opponent is only slightly ahead (denial).
            v = adv * 200 - us_d
            if adv < 0:
                v += (opp_d - us_d) * 20  # still cares about denying
            # strong boost for immediate capture
            if us_d == 0:
                v += 10**6
            # small tie-break by bias toward center-ish to reduce symmetry
            v -= abs(nx - (w // 2)) + abs(ny - (h // 2)) * 0.01
            if v > best_cell:
                best_cell = v
        # keep overall tie-break deterministic
        v_all = best_cell
        if v_all > bestv or (v_all == bestv and (dx, dy) < best):
            bestv = v_all
            best = (dx, dy)

    return [best[0], best[1]]