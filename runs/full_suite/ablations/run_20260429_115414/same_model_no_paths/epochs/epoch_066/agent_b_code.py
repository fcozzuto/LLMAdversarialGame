def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def density(x, y):
        c = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    # Pick a deterministic target: closer for us, farther for opponent, avoid dense/blocked cells.
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = ds - 0.6 * do + 0.15 * density(rx, ry)
            key = (val, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1]
    else:
        # Fallback: move toward center-ish while keeping away from obstacles
        cx, cy = w // 2, h // 2
        target = (cx, cy)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    resource_set = set(resources)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = cheb(nx, ny, target[0], target[1])
        d_opp_to_t = cheb(ox, oy, target[0], target[1])
        d_to_opp = cheb(nx, ny, ox, oy)
        on_res = 1.0 if (nx, ny) in resource_set else 0.0
        # Prefer immediate pickup, then reduce distance to target; discourage getting too close to opponent.
        score = (5.0 * on_res) - (1.2 * d_to_t) + (0.25 * d_opp_to_t) - (0.10 * d_to_opp) - (0.05 * density(nx, ny))
        key = (-(score), dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]