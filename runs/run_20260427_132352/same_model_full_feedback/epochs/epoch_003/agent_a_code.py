def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b):
        dx = a[0] - b[0]; dx = -dx if dx < 0 else dx
        dy = a[1] - b[1]; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # If standing position is somehow invalid, stay.
    if not inb(sx, sy): return [0, 0]

    # When resources exist: maximize (opponent advantage - our distance), but also explicitly deny resources
    # that the opponent is closer to.
    best_move = (0, 0); best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            v = -10**12
        else:
            v = 0
            # Encourage moving generally toward whichever corner is better to close distance.
            v += 0.08 * cheb((nx, ny), (w - 1, h - 1)) * (-1)  # slight tie-breaker
            # Core scoring over resources
            for rx, ry in resources:
                if (rx, ry) in obstacles: 
                    continue
                sd = cheb((nx, ny), (rx, ry))
                od = cheb((ox, oy), (rx, ry))
                diff = od - sd  # positive means we are closer
                # Attack when we can win; deny when opponent can win.
                if diff >= 0:
                    v += 12.0 * diff - 1.0 * sd
                else:
                    v += 4.0 * diff  # still discourage being too far from contested items
            # Additional opponent pressure: avoid giving opponent immediate access if close.
            v -= 0.35 * cheb((nx, ny), (ox, oy))
        if v > best_val:
            best_val = v; best_move = (dx, dy)

    if resources:
        # If all moves blocked, stay (engine will keep us in place).
        return [best_move[0], best_move[1]]
    # No resources: chase opponent to contest space.
    tx, ty = ox, oy
    best = (0, 0); bestd = 10**9
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb((nx, ny), (tx, ty))
        if d < bestd:
            bestd = d; best = (dx, dy)
    return [best[0], best[1]]