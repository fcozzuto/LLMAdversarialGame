def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def dist(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da + db

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            mind = 10**9
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            rscore = 1000 - 20 * mind
        else:
            rscore = 0
        dopp = dist(nx, ny, ox, oy)
        oppscore = -2 * dopp
        # slight preference to move toward center if no resources
        centerscore = 0
        if not resources:
            cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
            dd = abs(nx - cx) + abs(ny - cy)
            centerscore = -1 * dd
        v = rscore + oppscore + centerscore
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        # guaranteed valid fallback
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best