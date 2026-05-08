def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", [0, 0])[:2]
    sx, sy = int(sx), int(sy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    self_t = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp = observation.get("opponent_position", [0, 0])[:2]
    ox, oy = int(opp[0]), int(opp[1])

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles and (x, y) not in self_t:
                unclaimed.append((x, y))

    targets = resources if resources else unclaimed
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_for(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if not inb(nx, ny):
            return -10**9
        best = -10**9
        for tx, ty in targets[:30]:
            d = abs(nx - tx) + abs(ny - ty)
            oppd = abs(nx - ox) + abs(ny - oy)
            val = -d + 0.15 * oppd
            if (tx, ty) in self_t:
                val -= 2
            if val > best:
                best = val
        if best == -10**9:
            best = 0
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = - (abs(nx - cx) + abs(ny - cy)) * 0.001
        return best + center_bias

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = best_for(nx, ny)
        if sc > best_score or (sc == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = sc
            best_move = [dx, dy]
    return best_move