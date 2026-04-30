def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y):
                obst.add((x, y))

    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y) and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def dist_cheb(a, b):
        dx = abs(a[0]-b[0]); dy = abs(a[1]-b[1])
        return dx if dx>dy else dy

    def choose_target():
        if not res:
            return None
        best = None
        bestd = 10**9
        for r in res:
            d = dist_cheb((sx,sy), r)
            if d < bestd:
                bestd = d; best = r
            elif d == bestd and r < best:
                best = r
        return best

    tx, ty = ox, oy
    target = choose_target()
    if target is not None:
        tx, ty = target

    # Prefer moving towards target while avoiding obstacles
    best_move = (0,0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        score = 0
        # closer to target
        if target is not None:
            score -= dist_cheb((nx, ny), (tx, ty))
        # avoid opponent proximity? discourage moving into opponent
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            score -= 1
        # encourage moving toward nearest resource if exists
        if res:
            closest = min(res, key=lambda p: dist_cheb((nx, ny), p))
            score -= dist_cheb((nx, ny), closest)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]