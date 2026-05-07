def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2; ax = -ax if ax < 0 else ax
        ay = y1 - y2; ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay

    if not resources:
        # Drift to shrink distance to opponent while staying safe
        best = (-(10**9), 10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            myd = cheb(nx, ny, ox, oy)
            key = (-(myd), 0, dx, dy)
            if key > best[:4]:
                best = (key[0], key[1], key[2], key[3])
        return [best[2], best[3]]

    res = [tuple(r) for r in resources]
    best_move = (-(10**18), 10**18, 0, 0)  # (score, tie, dx, dy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        min_my = 10**18
        min_opp = 10**18
        best_margin = -(10**18)
        closest_secure_my = 10**18
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            margin = opd - myd  # positive => we are closer than opponent to this resource
            if margin > best_margin:
                best_margin = margin
            if myd < min_my: min_my = myd
            if opd < min_opp: min_opp = opd
            if margin >= 0 and myd < closest_secure_my:
                closest_secure_my = myd

        # Strategy: prefer moves that create the best advantage; if none, minimize opponent-danger.
        # Secondary: actually get closer to a "secure" resource if possible, else closest-to-some resource.
        if closest_secure_my < 10**18:
            tie = closest_secure_my
        else:
            tie = min_my + (2 * max(0, -best_margin))  # penalize poor advantage

        # Add tiny deterministic directional bias to break ties stably (favor up/left order of dirs list)
        score = best_margin * 1000 - tie + (dx * 0 + dy * 0)
        if score > best_move[0] or (score == best_move[0] and tie < best_move[1]):
            best_move = (score, tie, dx, dy)

    return [best_move[2], best_move[3]]