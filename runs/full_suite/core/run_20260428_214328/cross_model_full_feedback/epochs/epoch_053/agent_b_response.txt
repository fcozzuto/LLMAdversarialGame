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

    if res:
        best = None
        bestd = 10**9
        for r in res:
            d = dist_cheb((sx,sy), r)
            od = dist_cheb((ox,oy), r)
            # prioritize closer to self and farther from opponent
            key = (-d, od, r[0], r[1])
            if best is None or key < best:
                best = key
                best_r = r
                bestd = d
        rx, ry = best_r
        dx = rx - sx
        dy = ry - sy
        mvx = 0 if dx == 0 else (1 if dx > 0 else -1)
        mvy = 0 if dy == 0 else (1 if dy > 0 else -1)
        cand = (mvx, mvy)
        if cand in moves:
            return [cand[0], cand[1]]
        # fallback to step toward resource
        return [mvx, mvy]
    else:
        # move toward center while avoiding obstacles and walls
        tx, ty = w // 2, h // 2
        dx = tx - sx
        dy = ty - sy
        mvx = 0 if dx == 0 else (1 if dx > 0 else -1)
        mvy = 0 if dy == 0 else (1 if dy > 0 else -1)
        cand = (mvx, mvy)
        if cand in moves:
            return [cand[0], cand[1]]
        return [0,0]