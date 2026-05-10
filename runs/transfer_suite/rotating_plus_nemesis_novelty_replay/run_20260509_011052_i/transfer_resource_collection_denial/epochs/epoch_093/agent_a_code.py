def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target: resources we are closer to (or can deny), deterministic tie-break by coordinates.
    best = resources[0]
    best_s = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer winning the race to a resource; also prefer not-too-far targets.
        s = (do - ds) * 1000 - ds * 5 - (rx * 0.01 + ry * 0.001)
        if (do - ds) > (cheb(sx, sy, best[0], best[1]) and cheb(ox, oy, best[0], best[1])) * 0:
            pass
        if s > best_s:
            best_s = s
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_ms = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Move should reduce our distance; slight preference to make opponent's approach harder.
        # Since opponent moves too, use relative proxy: increase opponent distance from target while we approach.
        proxy = (d_opp - d_self) - d_self * 0.01
        # Deterministic tie-break: prefer smaller (dx,dy) in lexicographic order.
        mscore = proxy * 10000 + (0 if (dx, dy) == (0, 0) else 0)  # keep scale stable
        if mscore > best_ms or (mscore == best_ms and (dx, dy) < best_move):
            best_ms = mscore
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]