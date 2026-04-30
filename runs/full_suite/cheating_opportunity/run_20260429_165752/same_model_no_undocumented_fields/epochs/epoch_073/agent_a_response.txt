def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy))

    if not cand:
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    # Drift if no known resources
    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        bestv = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            # prefer closer to center; also keep away from opponent
            v = (cheb(nx, ny, cx, cy), -cheb(nx, ny, ox, oy), dx, dy)
            if best is None or v < bestv:
                best, bestv = (dx, dy), v
        return [best[0], best[1]]

    # Pick a target where we can gain tempo over opponent (or at least contest deterministically)
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        advantage = do - ds  # positive is good
        # Prefer maximum advantage; tie-break by closer-to-us and then by coordinates
        key = (-advantage, ds, rx, ry)
        if best_target is None or key < best_key:
            best_target, best_key = (rx, ry), key

    tx, ty = best_target
    best_move = None
    best_key2 = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        ds2 = cheb(nx, ny, tx, ty)
        # Evaluate resulting tempo advantage vs opponent; assume opponent stays (deterministic heuristic)
        do2 = cheb(ox, oy, tx, ty)
        adv2 = do2 - ds2
        # Also slightly prefer moves that increase distance from opponent if tempo is equal
        key2 = (-adv2, ds2, -cheb(nx, ny, ox, oy), dx, dy)
        if best_move is None or key2 < best_key2:
            best_move, best_key2 = (dx, dy), key2

    return [best_move[0], best_move[1]]