def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    if not resources:
        # Move toward center while avoiding obstacles
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = None
        best_score = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                score = - (abs(nx - w//2) + abs(ny - h//2))
                if score > best_score:
                    best_score = score
                    best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    my_pos = (sx, sy)
    op_pos = (ox, oy)

    best_r = None
    best_d = None
    for r in resources:
        d = cheb(op_pos, r)
        if best_d is None or d < best_d:
            best_d = d
            best_r = r

    d_to_r = cheb(my_pos, best_r) if best_r is not None else 10**9

    # If we can contest the nearest resource, head toward it (simple interception heuristic)
    if best_r is not None and d_to_r <= best_d:
        tx, ty = best_r
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obst:
            # avoid obstacle by trying alternative step
            alt = [(0,0), (dx,0), (0,dy), (dx,dy)]
            for ax, ay in alt:
                nx, ny = sx + ax, sy + ay
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                    return [ax, ay]
        return [dx, dy]

    # Otherwise, move toward center while avoiding obstacles
    dx = 0
    dy = 0
    if sx < w//2: dx = 1
    elif sx > w//2: dx = -1
    if sy < h//2: dy = 1
    elif sy > h//2: dy = -1

    # Try to step that is not blocked, otherwise stay or adjust
    for adx in [dx, 0, -dx]:
        for ady in [dy, 0, -dy]:
            nx, ny = sx + adx, sy + ady
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                return [adx, ady]

    return [0, 0]