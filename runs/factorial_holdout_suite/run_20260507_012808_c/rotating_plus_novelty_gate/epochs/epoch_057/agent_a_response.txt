def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    if sx < 0: sx = 0
    if sy < 0: sy = 0
    if ox < 0: ox = 0
    if oy < 0: oy = 0
    if sx >= w: sx = w - 1
    if sy >= h: sy = h - 1
    if ox >= w: ox = w - 1
    if oy >= h: oy = h - 1

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h: 
            return False
        return (nx, ny) not in obstacles

    steps = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        tx, ty = w - 1, h - 1
        bx = 1 if tx > sx else (-1 if tx < sx else 0)
        by = 1 if ty > sy else (-1 if ty < sy else 0)
        for dx, dy in steps:
            nx, ny = sx + dx, sy + dy
            if move_valid(nx, ny) and (dx == bx or dx == 0) and (dy == by or dy == 0):
                return [dx, dy]
        return [bx, by]

    best = None
    best_val = None
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not move_valid(nx, ny):
            continue
        # Evaluate immediate progress + "arrive first" pressure.
        local_best = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Primary: choose targets where we are at least as fast as opponent.
            # Secondary: maximize (opponent_distance - self_distance), then minimize our distance.
            val = (opd - myd) * 100 - myd
            # Tie-break deterministically toward closer-from-origin resources.
            val -= (rx * 9 + ry)
            if val > local_best:
                local_best = val
        # Prefer moves that also don't get dominated everywhere: small penalty if opponent is extremely close to nearest resource.
        nearest_opp = 10**9
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            if d < nearest_opp: nearest_opp = d
        local_best -= 0 if nearest_opp >= 2 else (2 - nearest_opp) * 3
        if best_val is None or local_best > best_val or (local_best == best_val and (dx*dx+dy*dy) < (best[0]*best[0]+best[1]*best[1])):
            best_val = local_best
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]