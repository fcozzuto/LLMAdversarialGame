def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                m += 1
        return m

    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    def nearest_corner_dist(px, py):
        best = None
        for cx, cy in corners:
            d = cheb(px, py, cx, cy)
            if best is None or d < best:
                best = d
        return best

    def best_corner(px, py, maximize):
        bestc = None
        bestv = None
        for cx, cy in corners:
            d = cheb(px, py, cx, cy)
            v = d if maximize else -d
            if bestv is None or v > bestv:
                bestv = v
                bestc = (cx, cy)
        return bestc

    scored_moves = []
    opp_corner = best_corner(ox, oy, maximize=False)
    far_corner_from_opp = best_corner(ox, oy, maximize=True)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        m = mobility(nx, ny)
        if pursuer:
            # Trap in the evader's nearest corner: become closer to that corner than the evader is.
            k1 = cheb(nx, ny, opp_corner[0], opp_corner[1])
            k2 = cheb(ox, oy, opp_corner[0], opp_corner[1])
            corner_adv = (k2 - k1)  # positive is good
            # Also reward alignment on x or y to limit escape.
            align = 1 if (nx == ox or ny == oy) else 0
            val = (-d * 1200) + (corner_adv * 120) + (align * 80) + m
        else:
            # Evade: maximize distance, move toward the farthest corner from the pursuer.
            farc = far_corner_from_opp
            k = cheb(nx, ny, farc[0], farc[1])
            val = (d * 1200) + (k * 60) + m - (nearest_corner_dist(nx, ny) * 20)

        scored_moves.append((val, dx, dy))

    if not scored_moves:
        return [0, 0]
    scored_moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = scored_moves[0]
    return [int(dx), int(dy)]