def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    if not targets:
        for p in (observation.get("opponent_territory") or []):
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))
    if not targets:
        return [0, 0]

    oterr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oterr.add((x, y))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = None
    bestv = None
    for x, y in targets:
        ds = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        do = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        adj_opp = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in oterr:
                adj_opp = 1
                break
        edge = abs(x - cx) + abs(y - cy)
        val = ds + 2 * edge + (0 if adj_opp else 25) - 0.6 * do
        if bestv is None or val < bestv or (val == bestv and (x, y) < best):
            bestv = val
            best = (x, y)

    tx, ty = best
    if tx == sx and ty == sy:
        return [0, 0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        # deterministic fallback: try axis-aligned toward target, else stay
        cand = []
        if nx >= 0 and nx < w and (nx, sy) not in obstacles:
            cand.append((nx, sy))
        if ny >= 0 and ny < h and (sx, ny) not in obstacles:
            cand.append((sx, ny))
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((nx, ny))
        if not cand:
            return [0, 0]
        tx2, ty2 = sorted(cand, key=lambda p: ((p[0]-tx)*(p[0]-tx)+(p[1]-ty)*(p[1]-ty), p))[0]
        return [tx2 - sx, ty2 - sy]

    return [dx, dy]