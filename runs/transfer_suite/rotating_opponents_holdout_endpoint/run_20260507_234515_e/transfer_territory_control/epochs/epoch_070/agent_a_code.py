def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed_list = observation.get("unclaimed_cells") or []
    unclaimed = set((int(x), int(y)) for x, y in unclaimed_list)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a deterministic target: prefer unclaimed frontier adjacent to our territory.
    frontier = []
    if self_terr and unclaimed:
        for (x, y) in unclaimed:
            ok = False
            for dx, dy in dirs:
                if (x + dx, y + dy) in self_terr:
                    ok = True
                    break
            if ok:
                frontier.append((x, y))
    pool = frontier if frontier else list(unclaimed) if unclaimed else []

    if pool:
        # Deterministic tie-break: (distance, x, y)
        tx, ty = min(pool, key=lambda p: (max(0, abs(p[0] - sx) + abs(p[1] - sy)), p[0], p[1]))
    else:
        # If nothing unclaimed, drift toward opponent territory or center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        if opp_terr:
            tx, ty = min(opp_terr, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        else:
            tx, ty = (int(cx), int(cy))

    best = (10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        if (nx, ny) in unclaimed:
            val = 6
        elif (nx, ny) in opp_terr:
            val = 4
        elif (nx, ny) in self_terr:
            val = 1
        else:
            val = 2
        # Prefer moves that reduce distance; slight preference for diagonal expansion
        score = (-val * 100) + dist * 1 + (0 if dx == 0 or dy == 0 else -0.1)
        key = (int(score), dx, dy)
        if key < best:
            best = key

    # If all neighbors invalid, stay.
    return [int(best[1]), int(best[2])] if best[0] != 10**9 else [0, 0]