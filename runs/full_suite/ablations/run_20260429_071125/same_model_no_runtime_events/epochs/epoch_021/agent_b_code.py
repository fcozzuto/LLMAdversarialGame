def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict):
            pos = r.get("pos")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
            elif "x" in r and "y" in r:
                x, y = r.get("x"), r.get("y")
                if x is not None and y is not None:
                    resources.append((int(x), int(y)))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = [0, 0, 10**9]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                # slight anti-stalemate: prefer moving away from opponent if possible
                d = abs(nx - ox) + abs(ny - oy)
                if d > best[2]:
                    best = [dx, dy, d]
        return [best[0], best[1]]

    # choose nearest resource by Manhattan
    tx, ty = None, None
    bestd = 10**9
    for x, y in resources:
        d = abs(x - sx) + abs(y - sy)
        if d < bestd:
            bestd = d
            tx, ty = x, y
    if tx is None:
        return [0, 0]

    # greedy step toward target; if blocked, pick valid move with minimal distance
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            dist = abs(tx - nx) + abs(ty - ny)
            # deterministic tie-break: prefer (dx0,dy0) direction, then smaller dx, then smaller dy
            dirscore = 0 if (dx == dx0 and dy == dy0) else 1
            cand.append((dist, dirscore, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    return [int(cand[0][2]), int(cand[0][3])]