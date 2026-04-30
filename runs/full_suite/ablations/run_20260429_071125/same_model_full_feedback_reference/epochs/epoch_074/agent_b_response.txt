def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    # pick a deterministic target: nearest resource, tie by closer to center, then by lexicographic
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            dc = cheb(cx, cy, rx, ry)
            key = (ds, dc, rx, ry)
            if best is None or key < best:
                best = key
                target = (rx, ry)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Heuristic components
        if target:
            d_to_t = cheb(nx, ny, target[0], target[1])
            d_now_t = cheb(sx, sy, target[0], target[1])
            improve = d_now_t - d_to_t  # prefer getting closer
            score = 1000 * improve - 3 * d_to_t
            # avoid letting opponent get closer to target
            d_opp = cheb(ox, oy, target[0], target[1])
            score -= 2 * (cheb(nx, ny, target[0], target[1]) <= d_opp)
            # slight bias toward center and away from opponent
            score -= 0.5 * cheb(nx, ny, ox, oy)
            score -= 0.1 * cheb(nx, ny, cx, cy)
        else:
            # no visible resources: move toward opponent side while staying safe-ish
            score = -cheb(nx, ny, ox, oy) + 0.2 * cheb(nx, ny, cx, cy)

        # obstacle proximity penalty (local, deterministic)
        ppen = 0
        for adx, ady in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            ax, ay = nx + adx, ny + ady
            if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in obstacles:
                ppen += 1
        score -= 0.05 * ppen

        if score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]