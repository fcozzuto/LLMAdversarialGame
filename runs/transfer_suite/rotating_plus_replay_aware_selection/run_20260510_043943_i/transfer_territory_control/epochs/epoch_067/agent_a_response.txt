def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                unclaimed.append((x, y))

    selfT = set((t[0], t[1]) for t in (observation.get("self_territory") or []))
    oppT = set((t[0], t[1]) for t in (observation.get("opponent_territory") or []))

    candidates = []
    for x, y in unclaimed:
        if (x, y) not in selfT and (x, y) not in obstacles:
            candidates.append((x, y))

    # Add cells adjacent to opponent territory to enable quick counterclaim
    for (tx, ty) in oppT:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = tx + dx, ty + dy
                if ok(nx, ny) and (nx, ny) not in selfT:
                    candidates.append((nx, ny))

    if not candidates:
        # Fallback: chase opponent if near, otherwise head to opposite corner
        tx, ty = (ox, oy) if (abs(ox - sx) + abs(oy - sy) <= 3) else (w - 1 if sx < w // 2 else 0, h - 1 if sy < h // 2 else 0)
        candidates = [(tx, ty)]

    # Choose move that improves territory gain potential: prefer cells where we are closer than opponent
    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # If moving into opponent territory, it's usually high value (flip-on-entry)
        in_opp = (nx, ny) in oppT
        in_un = (nx, ny) in selfT
        # Evaluate against top few nearest candidates for speed/determinism
        sd = 10**9
        od = 10**9
        for (tx, ty) in candidates[:30]:
            d1 = abs(tx - nx) + abs(ty - ny)
            d2 = abs(tx - ox) + abs(ty - oy)
            if d1 < sd:
                sd = d1
            if d2 < od:
                od = d2
        # Score: maximize advantage (opponent farther), while minimizing distance
        val = (20 if in_opp else 0) + (2 if (nx, ny) in selfT else 0) + (od - sd) * 3 - sd
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]