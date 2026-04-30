def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # Pick a target that we are comparatively closer to than opponent.
    targets = resources[:] if resources else []
    if not targets:
        # No resources visible: go toward the farther corner from our position relative to opponent
        target = (0, h - 1) if (sx + sy) <= (ox + oy) else (w - 1, 0)
    else:
        best_t = targets[0]
        best_key = None
        for tx, ty in targets:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Primary: minimize our distance; Secondary: beat opponent; Tertiary: prefer cells closer to center
            center_bias = cheb(tx, ty, (w - 1)//2, (h - 1)//2)
            key = (ds, do - ds, center_bias)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty)
        target = best_t

    tx, ty = target
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        # Compare advantage vs opponent if they move next (assume opponent can also step optimally)
        o_ds = cheb(ox, oy, tx, ty)
        # Small tie-breaker: discourage stepping away from target by using exact distance after move
        val = (ds, o_ds - ds, (nx - tx)*(nx - tx) + (ny - ty)*(ny - ty), dx*dx + dy*dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]