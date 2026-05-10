def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    rpos = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                rpos.append((x, y))
    if not rpos:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in rpos:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer (do - ds larger), then closer to us, then deterministically by coords.
        key = (do - ds, -ds, -rx, -ry)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key
    tx, ty = best

    candidates = []
    for dx, dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            d = cheb(nx, ny, tx, ty)
            # Bias to not step into giving opponent a winning grab: slightly reward increasing opponent distance to that target.
            do_next = cheb(ox, oy, tx, ty)
            # Deterministic ordering even when do_next constant: use nx,ny.
            candidates.append((d, -(do_next), nx, ny, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][4]), int(candidates[0][5])]