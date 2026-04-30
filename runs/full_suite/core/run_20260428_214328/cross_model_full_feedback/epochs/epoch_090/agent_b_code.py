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

    # simple heuristic: move toward the nearer resource if any, else move toward opponent to contest, avoiding obstacles
    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # possible moves
    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    best = (0,0)
    best_score = 10**9

    if resources:
        # target nearest resource
        nearest = None
        nd = 10**9
        for r in resources:
            d = dist((sx,sy), r)
            if d < nd:
                nd = d
                nearest = r
        tx, ty = nearest
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if 0 <= nx < w and 0 <= ny < h and (nx,ny) not in obst:
                d = dist((nx,ny), (tx,ty))
                if d < best_score:
                    best_score = d
                    best = (dx, dy)
        return [best[0], best[1]]
    else:
        # no resources: approach opponent to contest
        target = (ox, oy)
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if 0 <= nx < w and 0 <= ny < h and (nx,ny) not in obst:
                d = dist((nx,ny), target)
                if d < best_score:
                    best_score = d
                    best = (dx, dy)
        return [best[0], best[1]]