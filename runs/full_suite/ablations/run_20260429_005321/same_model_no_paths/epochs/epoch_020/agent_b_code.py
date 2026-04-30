def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dist = cheb(nx, ny, ox, oy)
            free = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if valid(tx, ty): free += 1
            val = dist * 100 + free
            if val > best[2]: best = (dx, dy, val)
        return [best[0], best[1]]

    # If already on a resource, stay to collect.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # Pick a contested target: maximize how much closer we are than opponent.
    best_t = None; best_adv = -10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # Small tie-break: prefer nearer to us to start pressure.
        if adv > best_adv or (adv == best_adv and sd < cheb(sx, sy, resources[0][0], resources[0][1])):
            best_adv = adv
            best_t = (rx, ry)

    tx, ty = best_t
    old_sd = cheb(sx, sy, tx, ty)
    old_od = cheb(ox, oy, tx, ty)

    # Choose move that improves advantage; also avoid obstacle traps.
    best = (0, 0, -10**9)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)  # opponent not moving this turn; keep stable
        # If we reach target, prioritize heavily.
        reach = 1 if nds == 0 else 0
        free = 0
        for ddx, ddy in deltas:
            px, py = nx + ddx, ny + ddy
            if valid(px, py): free += 1
        # Advantage: bigger means opponent further relative to our progress.
        adv = ndo - nds
        # Prefer moves that decrease our distance to target and improve advantage.
        progress = old_sd - nds
        # Also lightly deter moving closer to opponent when not making progress.
        oppdist = cheb(nx, ny, ox, oy)
        val = adv * 1000 + progress * 50 + free * 3 + reach * 10**6 + oppdist
        if val > best[2]:
            best = (dx, dy, val)

    return [best[0], best[1]]