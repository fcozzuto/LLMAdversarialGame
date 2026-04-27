def choose_move(observation):
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a resource where we are relatively closer; if none, pick the most contested.
    best_r = None
    best_rel = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        rel = do - ds  # positive means we are closer
        if best_r is None or rel > best_rel or (rel == best_rel and ds < cheb(sx, sy, best_r[0], best_r[1])):
            best_r = (rx, ry)
            best_rel = rel
    rx, ry = best_r

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Determine if we should actively avoid opponent when they are too close.
    dist_opp = cheb(sx, sy, ox, oy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_new = cheb(nx, ny, rx, ry)
        do_same = cheb(ox, oy, rx, ry)
        # Main goal: minimize our distance to chosen resource while keeping relative advantage.
        val = ds_new - (do_same - ds_new) * 0.25
        # If opponent is extremely close, avoid moving into their neighborhood.
        if dist_opp <= 1:
            dp_new = cheb(nx, ny, ox, oy)
            val += (2.5 - dp_new) * 0.8
        # Slight tie-breaker: prefer moves that also reduce distance to the opponent when we're far (potential blocking).
        if dist_opp >= 3:
            dp_new = cheb(nx, ny, ox, oy)
            val += dp_new * 0.05
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]