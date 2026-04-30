def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def dist_cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    def in_bounds(x,y):
        return 0 <= x < w and 0 <= y < h

    best = (0,0)
    best_score = None

    def score_move(nx, ny):
        if not in_bounds(nx, ny): 
            return None
        if (nx, ny) in obst:
            return None
        # prefer closer to a resource, then closer to opponent to contest
        s = 0
        if resources:
            d = min(dist_cheb((nx,ny), r) for r in resources)
            s -= d * 2
        d_op = dist_cheb((nx,ny), (ox,oy))
        s -= d_op
        return s

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sc = score_move(nx, ny)
            if sc is None:
                continue
            if best_score is None or sc > best_score:
                best_score = sc
                best = (dx, dy)
    else:
        # chase opponent corner deterministically
        tx = 0 if ox >= w // 2 else w - 1
        ty = 0 if oy >= h // 2 else h - 1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obst:
                continue
            # move toward target corner
            cur = (abs(nx - tx) + abs(ny - ty))
            if best_score is None or cur < best_score:
                best_score = cur
                best = (dx, dy)

    dx, dy = best
    return [dx, dy]