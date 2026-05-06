def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a denial target: resources where we are relatively closer than the opponent.
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = (do - ds, -ds, -(rx + ry))
            if best is None or val > best[0]:
                best = (val, (rx, ry), ds, do)
        tx, ty = best[1] if best is not None else (ox, oy)
    else:
        tx, ty = ox, oy

    # If opponent is strictly closer to all resources, switch to interception.
    intercept = True
    if resources:
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            if cheb(sx, sy, rx, ry) <= cheb(ox, oy, rx, ry):
                intercept = False
                break

    best_move = (0, 0)
    best_val = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_to_t = cheb(nx, ny, tx, ty)
        opp_to_t = cheb(ox, oy, tx, ty)
        if intercept:
            # Intercept: reduce distance to opponent while keeping reasonably toward their current target.
            v1 = (self_to_t - cheb(nx, ny, ox, oy))  # smaller is better, we invert later
            val = (-v1, -self_to_t, -cheb(nx, ny, ox, oy))
        else:
            # Deny: maximize (opp_d - self_d) and then minimize our distance to target.
            val = (opp_to_t - self_to_t, -self_to_t, -cheb(nx, ny, ox, oy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]