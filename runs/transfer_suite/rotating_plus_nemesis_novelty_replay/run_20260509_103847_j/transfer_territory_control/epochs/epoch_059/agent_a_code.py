def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0]); sx, sy = int(sx), int(sy)
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if len(p) >= 2)
    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if len(p) >= 2)
    opT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if len(p) >= 2)
    unT = []
    for p in (observation.get("unclaimed_cells") or []):
        if len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.append((x, y))
    if not unT:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    unSet = set(unT)
    frontier = []
    for x, y in selfT:
        for nx, ny in neigh8(x, y):
            if (nx, ny) in unSet:
                frontier.append((nx, ny))
    frontier = list(set(frontier))

    # Prefer capturing openings near opponent edges/territory, but expand our frontier first.
    def score_cell(p):
        x, y = p
        center = abs(x - cx) + abs(y - cy)
        adj_op = 0
        adj_self = 0
        for nx, ny in neigh8(x, y):
            if (nx, ny) in opT: adj_op += 1
            if (nx, ny) in selfT: adj_self += 1
        # Edge-claim opponent: block by taking cells near their territory and not too close to map corners.
        corner_pen = min(x, y, w - 1 - x, h - 1 - y)
        return (0 if p in frontier else 1, -adj_op, -adj_self, center, -corner_pen)

    targets = frontier if frontier else unT
    best_target = min(targets, key=score_cell)

    # Choose a deterministic move step that approaches best_target, avoiding obstacles if possible.
    tx, ty = best_target
    best_move = [0, 0]
    best_val = (10**9, 10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to target; Secondary: prefer moves adjacent to opponent territory to enable flips.
        dist = abs(nx - tx) + abs(ny - ty)
        adj_op = 0
        for ax, ay in neigh8(nx, ny):
            if (ax, ay) in opT: adj_op += 1
        val = (dist, -adj_op)
        if val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move if best_move != [0, 0] or (sx, sy) == (tx, ty) else [0, 0]