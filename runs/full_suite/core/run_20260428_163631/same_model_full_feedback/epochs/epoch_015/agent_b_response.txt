def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free_neighbors(x, y):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0: continue
            nx, ny = x + dx, y + dy
            if safe(nx, ny): c += 1
        return c

    if resources:
        best_r = resources[0]
        best_score = -10**18
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if opd == myd:
                s = -myd
            else:
                s = (opd - myd) * 3 - myd * 0.7
                if opd < myd: s -= 6
            # slight bias toward closer overall
            s -= 0.02 * (rx + ry)
            if s > best_score:
                best_score, best_r = s, (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        od = cheb(nx, ny, ox, oy)
        # contest: don't give opponent easy access to your target; but also avoid getting stuck
        # prefer reducing target distance, prefer staying mobile, keep some distance from opponent
        val = -d * 2.2 + free_neighbors(nx, ny) * 0.35 + od * 0.04
        if resources:
            # if opponent can reach target much sooner, reduce distance to a nearby alternative by looking at opponent reach
            opd = cheb(ox, oy, tx, ty)
            myd2 = cheb(nx, ny, tx, ty)
            if myd2 > opd - 1:
                val -= (myd2 - opd) * 1.0
        if val > best_val:
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]