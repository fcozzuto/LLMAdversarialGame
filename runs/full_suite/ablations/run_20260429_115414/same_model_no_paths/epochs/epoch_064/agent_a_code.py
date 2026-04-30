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

    def adj_obs(x, y):
        c = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; tie-break deterministically by position.
        key = (1 if do < ds else 0, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    if target is None:
        # No visible resources: drift deterministically toward the center.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        target = (tx, ty)

    tx, ty = target
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        # Move closer to target, discourage getting too close to opponent, avoid obstacle adjacency.
        score = -2 * ds + 0.35 * do - 0.7 * adj_obs(nx, ny)
        # Small deterministic tiebreak: favor lower dx, then lower dy.
        tieb = (dx, dy)
        if best is None or score > best[0] or (score == best[0] and tieb < best[1]):
            best = (score, tieb)
    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]