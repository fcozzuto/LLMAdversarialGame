def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = dist(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return [int(best[0]), int(best[1])]

    # Choose target resource to "steal": maximize (opp_dist - my_dist)
    target = resources[0]
    best_steal = -10**9
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        steal = opd - myd
        if steal > best_steal:
            best_steal = steal
            target = (rx, ry)

    rx, ry = target
    best = [0, 0]
    bestv = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = dist(nx, ny, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # Prefer reducing my distance to target, and prefer increasing opponent distance to it
        v = (opd - myd) * 2 + dist(nx, ny, ox, oy) - (1 if (nx, ny) == (sx, sy) else 0)
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return [int(best[0]), int(best[1])]