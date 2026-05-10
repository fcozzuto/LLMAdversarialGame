def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))

    unT = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_score = -10**9

    def adj_count(x, y, S):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in S:
                    c += 1
        return c

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if (nx, ny) in selfT:
            base = 0.0
        elif (nx, ny) in opT:
            base = 1.0 + 0.6 * adj_count(nx, ny, opT)
        elif (nx, ny) in unT:
            base = 1.0
        else:
            base = 0.1

        own_adj = adj_count(nx, ny, selfT)
        op_adj = adj_count(nx, ny, opT)

        free_adj = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and ((tx, ty) in unT or (tx, ty) in opT):
                    free_adj += 1

        cx, cy = (nx - (w - 1) / 2.0), (ny - (h - 1) / 2.0)
        center_bonus = 0.03 * (16.0 - (cx * cx + cy * cy))

        score = base + 0.35 * own_adj + 0.25 * free_adj - 0.18 * op_adj + center_bonus

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best