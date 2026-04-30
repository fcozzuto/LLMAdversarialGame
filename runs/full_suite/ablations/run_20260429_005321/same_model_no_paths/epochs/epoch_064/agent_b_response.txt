def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    steps = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_t = None
    best_score = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets we reach sooner; if tied, prefer closer.
        s = (do - ds) * 10 - ds
        # Small bias away from resources that are adjacent to obstacles (fragile paths).
        adj = 0
        for ddx in (-1, 0, 1):
            nx = rx + ddx
            for ddy in (-1, 0, 1):
                ny = ry + ddy
                if (nx, ny) in obstacles:
                    adj += 1
        s -= adj
        if s > best_score:
            best_score = s
            best_t = (rx, ry)

    tx, ty = best_t
    candidates = []
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Choose move that improves our distance to target while reducing opponent pressure.
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        opp_future = do - cheb(ox, oy, nx, ny)
        score = -ds * 5 + (do - ds) * 2 - opp_future
        # Bonus if the move blocks an adjacent capture square for the opponent.
        if do == 1:
            score += 1
        candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]