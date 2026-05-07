def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    obstacles = observation.get("obstacles") or []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if ok(tx, ty):
                targets.append((tx, ty))

    if targets:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = -10**18
            for tx, ty in targets:
                ds = man(nx, ny, tx, ty)
                do = man(ox, oy, tx, ty)
                v = do - ds
                if v > score:
                    score = v
            if score > bestv:
                bestv = score
                best = (dx, dy)
        return [best[0], best[1]]

    cx, cy = w // 2, h // 2
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = -man(nx, ny, cx, cy)  # deterministic: closer to center
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]