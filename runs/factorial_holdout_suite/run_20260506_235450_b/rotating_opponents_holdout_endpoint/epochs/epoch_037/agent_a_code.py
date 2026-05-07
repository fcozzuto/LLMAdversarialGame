def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        x = y = None
        if isinstance(a, dict):
            if "x" in a and "y" in a:
                x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        if x is not None and 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x = y = None
        if isinstance(r, dict):
            if "x" in r and "y" in r:
                x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        if x is not None and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx + dy - min(dx, dy)  # L1-ish but deterministic

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dcur = abs(sx - ox) + abs(sy - oy)
            dnxt = abs(nx - ox) + abs(ny - oy)
            v = dnxt - dcur
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    target = resources[0]
    best = 10**18
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = ds - do  # prefer where we are relatively closer
        if score < best:
            best = score
            target = (rx, ry)

    tx, ty = target
    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) == (tx, ty):
            return [dx, dy]
        v = -(dist((nx, ny), (tx, ty)))
        opp_close = (abs(nx - ox) + abs(ny - oy)) <= 2
        if opp_close:
            v -= 2  # slight retreat when very close to opponent
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best if best is not None else [0, 0]