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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return (ox, oy)
        best_cell = None
        best_val = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources opponent is farther from, but still not too far from us.
            val = (do - ds, -ds, -(rx + ry))
            if best_cell is None or val > best_val:
                best_cell = (rx, ry)
                best_val = val
        return best_cell if best_cell is not None else (ox, oy)

    tx, ty = best_target()

    def score_cell(x, y):
        ds = cheb(x, y, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Add a small "sweeping" term toward the nearest remaining resource overall.
        nearest = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = cheb(x, y, rx, ry)
            if d < nearest:
                nearest = d
        # Main objective: beat opponent on the target and also reduce our nearest-resource distance.
        return (do - ds) * 10 - ds - 0.5 * nearest

    best_move = (0, 0)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        s = score_cell(nx, ny)
        if s > best_s:
            best_s = s
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]