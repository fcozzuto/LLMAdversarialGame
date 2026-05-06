def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                v = cheb(nx, ny, tx, ty) + 0.01 * cheb(nx, ny, ox, oy)
                if v < bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Choose the contest advantage resource from this next cell.
        # Prefer moves that create a positive (self closer than opponent) margin.
        best_r_adv = -10**18
        best_r_fallback = 10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_r_adv:
                best_r_adv = adv
            if ds < best_r_fallback:
                best_r_fallback = ds

        # If we can contest (adv>0), maximize it; otherwise minimize our distance (fallback).
        val = best_r_adv
        if val <= 0:
            val = -best_r_fallback - 0.01 * cheb(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move