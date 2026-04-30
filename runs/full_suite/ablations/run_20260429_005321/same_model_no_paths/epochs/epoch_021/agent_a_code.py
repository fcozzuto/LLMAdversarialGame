def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if any(sx == rx and sy == ry for rx, ry in resources):
        return [0, 0]

    # Choose a contested target: the resource where we are relatively closest vs opponent.
    if resources:
        best_t = resources[0]; best_rel = -10**9
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry); opd = cheb(ox, oy, rx, ry)
            rel = opd - myd
            if rel > best_rel:
                best_rel = rel; best_t = (rx, ry)
    else:
        best_t = None

    # If no resources, drift toward center while keeping distance from opponent.
    if best_t is None:
        tx, ty = (w - 1) / 2, (h - 1) / 2
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dist_center = cheb(nx, ny, tx, ty)
            dist_opp = cheb(nx, ny, ox, oy)
            score = dist_opp * 2 - dist_center
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    rx, ry = best_t

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        rel = opd - myd  # higher means we're closer than opponent

        # Block by reducing opponent's access to this target and by maintaining adjacency pressure.
        opp_after = cheb(nx, ny, ox, oy)
        my_to_opp = cheb(nx, ny, ox, oy)

        # Local mobility (avoid tight spots).
        free = 0
        for ddx, ddy in deltas:
            tx2, ty2 = nx + ddx, ny + ddy
            if valid(tx2, ty2):
                free += 1

        # If we can reach the target immediately, prioritize strongly.
        immediate = 1 if myd == 0 else 0

        score = (rel * 120) - (myd * 5) + (free * 2) + (immediate * 10000) - (my_to_opp * 0.5)
        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]