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

    # If there is a reachable resource, head towards the closest one while keeping some spacing from opponent
    if res:
        best = None
        bestd = 10**9
        for r in res:
            d = dist_cheb((sx,sy), r)
            if d < bestd:
                bestd = d; best = r
        tx, ty = best
        dx = sign(tx - sx)
        dy = sign(ty - sy)
        cand = (dx, dy)
        # avoid obstacle or out of bounds by adjusting one step if blocked
        nx, ny = sx + cand[0], sy + cand[1]
        if not inside(nx, ny) or (nx, ny) in obst:
            # try staying or moving along alternative axis
            for ax, ay in [(dx,0),(0,dy),(-dx,-dy)]:
                tx2, ty2 = sx + ax, sy + ay
                if inside(tx2, ty2) and (tx2, ty2) not in obst:
                    return [ax, ay]
            return [0,0]
        return [cand[0], cand[1]]

    # No resources: approach center away from obstacle cluster and keep distance from opponent
    # Move towards a square that reduces Chebyshev distance to center while not stepping into obstacle or opponent too closely
    center = (w//2, h//2)
    dx = sign(center[0] - sx)
    dy = sign(center[1] - sy)
    cand = (dx, dy)
    nx, ny = sx + cand[0], sy + cand[1]
    if inside(nx, ny) and (nx, ny) not in obst:
        # also avoid stepping onto opponent
        if (nx, ny) != (ox, oy):
            return [cand[0], cand[1]]
    # Fallback: try all 9 moves in a deterministic priority near current position
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy):
            return [mx, my]
    return [0,0]