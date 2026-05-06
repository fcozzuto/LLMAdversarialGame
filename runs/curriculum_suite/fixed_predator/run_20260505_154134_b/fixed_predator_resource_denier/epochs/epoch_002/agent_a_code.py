def choose_move(observation):
    w, h = observation.get('grid_width', 8), observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Choose a target resource that we can reach sooner than the opponent (resource denial)
    if resources:
        best_r = None
        best_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obstacles:
                continue
            da = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer large advantage (opponent farther), then nearer for us, then tie-breaker by coords
            key = (do - da, -da, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        if best_r is None:
            target = (ox, oy)
        else:
            target = best_r
    else:
        target = (ox, oy)

    tx, ty = target
    moves = [(1, 1), (1, 0), (1, -1), (0, 1), (0, 0), (0, -1), (-1, 1), (-1, 0), (-1, -1)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Keep opponent pressure low: maximize (od - myd)
        # Also penalize wandering: prefer smaller myd
        val = ((od - myd), (-myd), -cheb(nx, ny, ox, oy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves invalid (surrounded by obstacles), try to stay
    if best_val is None:
        return [0, 0]
    return [best_move[0], best_move[1]]