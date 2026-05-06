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
        tx, ty = w - 1, h - 1
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 1000 - (abs(nx - tx) + abs(ny - ty))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18

    # Intercept/delay policy: maximize lead over opponent on some resource; if none winnable, reduce their lead most.
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        best_r = -10**18
        # small deterministic tie-break by preferring lower dS when equal
        for rx, ry in resources:
            dS = cheb(nx, ny, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            margin = dO - dS  # positive => we are closer than opponent to that resource
            # strong weight on making at least one resource winnable; otherwise deny closest opponent pressure
            v = margin * 120 - dS
            if margin < 0:
                v += margin * 60  # larger penalty if still behind
            # slight preference to reduce our distance when close outcomes are equal
            v -= (1 if (nx == rx and ny == ry) else 0) * 0.5
            if v > best_r or (v == best_r and dS < cheb(x, y, rx, ry)):
                best_r = v
        # Also discourage stepping into cells where we're far from every resource relative to opponent
        fallback = -min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        vtotal = best_r + fallback * 0.01
        if vtotal > bestv or (vtotal == bestv and (dx, dy) < best):
            bestv = vtotal
            best = (dx, dy)

    return [best[0], best[1]]