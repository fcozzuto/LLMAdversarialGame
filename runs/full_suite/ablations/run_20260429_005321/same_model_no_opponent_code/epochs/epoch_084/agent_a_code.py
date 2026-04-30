def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # Select best resource: prioritize ones we can reach first
    best_r = None
    best_val = -10**18
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Strongly favor positive gap; lightly penalize longer distances
        gap = do - ds
        val = gap * 2000 - ds
        if gap == 0:
            val -= cheb(sx, sy, rx, ry) // 2
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    rx, ry = best_r
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    # If a reachable move can immediately collect (adjacent/at), pick the first such move deterministically
    for dx, dy, nx, ny in legal:
        if (nx, ny) in res:
            return [dx, dy]

    # Otherwise greedily minimize our distance to target, with tie-breakers to maximize our advantage
    best = None
    best_key = None
    for dx, dy, nx, ny in legal:
        ns = cheb(nx, ny, rx, ry)
        no = cheb(ox, oy, rx, ry)
        gap = no - ns
        key = (gap, -ns, -abs((nx - rx)) - abs((ny - ry)))
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]