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

    def sign(a): return -1 if a<0 else (1 if a>0 else 0)

    def best_move_towards(target):
        tx, ty = target
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obst:
                continue
            myd = dist_cheb((sx, sy), (tx, ty))
            ndist = dist_cheb((nx, ny), (tx, ty))
            gain = myd - ndist
            # prefer larger gain, then closer to target
            score = (gain, -ndist)
            if best is None or score > best_score:
                best = (nx, ny)
                best_score = score
        if best is None:
            return (sx, sy)
        return best

    if res:
        best_r = None
        best_key = None
        for rx, ry in res:
            myd = dist_cheb((sx, sy), (rx, ry))
            opd = dist_cheb((ox, oy), (rx, ry))
            gap = opd - myd
            key = (gap, -myd, ry, rx)
            if best_r is None or key > best_key:
                best_r = (rx, ry); best_key = key
        target = best_r
        nx, ny = best_move_towards(target)
    else:
        target = (w // 2, h // 2)
        nx, ny = best_move_towards(target)

    dx = nx - sx
    dy = ny - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [dx, dy]