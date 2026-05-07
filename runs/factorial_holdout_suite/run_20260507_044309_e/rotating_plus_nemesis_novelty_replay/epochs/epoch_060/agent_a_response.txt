def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = []
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        candidates.append((adv, ds, rx, ry))
    if not candidates:
        return [0, 0]

    # Best target: maximize advantage; break ties toward closer and then deterministic position order
    candidates.sort(key=lambda t: (t[0], -t[1], -t[2], -t[3]), reverse=True)
    target = candidates[0][2], candidates[0][3]
    tx, ty = target

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Compute new advantage for the same target
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        adv = no - ns

        # Small obstacle-avoidance + resource densification: prefer moves with fewer blocked adjacent cells
        blocked = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if ax < 0 or ax >= w or ay < 0 or ay >= h:
                continue
            if (ax, ay) in obstacles:
                blocked += 1

        # Also consider moving toward any nearby resource, not just the chosen target
        best_other = 10**9
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            d = cheb(nx, ny, rx, ry)
            if d < best_other:
                best_other = d

        key = (adv, -ns, -best_other, -blocked, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        # Fallback: try any non-obstacle in-bounds move that reduces distance to chosen target
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if cheb(nx, ny, tx, ty) <= cheb(sx, sy, tx, ty):
                    return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]