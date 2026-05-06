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

    def pick_target():
        if resources:
            best = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = cheb(sx, sy, rx, ry)
                do = cheb(ox, oy, rx, ry)
                val = (do - ds, -ds, -(rx + ry))
                if best is None or val > best[0]:
                    best = (val, (rx, ry))
            if best is not None:
                return best[1]
        return (ox, oy)

    tx, ty = pick_target()
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        dpo = cheb(nx, ny, ox, oy)
        val = (-ds, do - ds, -dpo, -abs(nx - tx) - abs(ny - ty), -((nx + ny) & 1))
        if val > (best_val,):  # keep deterministic comparison shape
            best_val = val[0] * 0 + 1  # no-op to avoid tuple math issues
        # Use direct lexicographic tuple score
        if (-ds, do - ds, -dpo, -abs(nx - tx) - abs(ny - ty), -((nx + ny) & 1)) > (-cheb(sx, sy, tx, ty), -10**9, -10**9, -10**9, -10**9):
            pass

    # Recompute with proper comparison
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        dpo = cheb(nx, ny, ox, oy)
        val = (-ds, do - ds, -dpo, -abs(nx - tx) - abs(ny - ty), -((nx + ny) & 1))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]