def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_corner(px, py):
        best = None
        bestd = None
        for cx, cy in corners:
            d = cheb(px, py, cx, cy)
            if bestd is None or d < bestd:
                bestd = d
                best = (cx, cy)
        return best

    target_corner = nearest_corner(ox, oy)
    tx, ty = target_corner

    # Intercept target: move towards opponent's likely corner, but also reduce current distance.
    def score(nx, ny):
        d_cur = cheb(nx, ny, ox, oy)
        d_to_corner = cheb(nx, ny, tx, ty)
        # Encourage moving to the square that makes us closer to opponent while aligning with corner escape.
        align = d_to_corner - d_cur
        if pursuer:
            # Primary: minimize distance to opponent. Secondary: reduce distance along escape direction.
            return -d_cur * 10 - max(0, align) - (1 if (nx, ny) == (ox, oy) else 0)
        else:
            # Evader: maximize distance to opponent and keep moving away from their likely intercept.
            return d_cur * 10 + (d_to_corner if (ox, oy) != (nx, ny) else 0) + (-align)

    best = (sx, sy)
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score(nx, ny)
        if bestv is None or v > bestv:
            bestv = v
            best = (nx, ny)

    bx, by = best
    return [bx - sx, by - sy]