def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
    if not resources:
        best = (0, 0, -10**18)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = -cheb(nx, ny, ox, oy)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    # New policy: "secure-now" advantage. Prefer moves where we are closer (chebyshev) to a resource than opponent.
    best = (0, 0, -10**18, 10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        best_adv = -10**18
        best_sd = 10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer
            if adv > best_adv or (adv == best_adv and sd < best_sd):
                best_adv, best_sd = adv, sd

        # If no positive advantage exists, still move towards the closest resource (best_sd).
        # Tie-breakers: prefer larger best_adv, then smaller best_sd, then deterministic dir order via > comparisons.
        val_adv = best_adv
        val_sd = best_sd
        if (val_adv > best[2]) or (val_adv == best[2] and val_sd < best[3]):
            best = (dx, dy, val_adv, val_sd)

    return [best[0], best[1]]