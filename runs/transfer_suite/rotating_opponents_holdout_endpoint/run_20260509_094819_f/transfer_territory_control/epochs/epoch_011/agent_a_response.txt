def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_count = int(observation.get("opponent_territory_count", 0) or 0)
    self_count = int(observation.get("self_territory_count", 0) or 0)
    aggressive = self_count >= opp_count

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Prefer stepping toward frontier: cells in unclaimed adjacent to our territory,
    # else toward nearest unclaimed, else toward opponent if aggressive.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    frontier = set()
    if self_terr:
        for (x, y) in self_terr:
            for ddx, ddy in dirs:
                tx, ty = x + ddx, y + ddy
                if inb(tx, ty) and (tx, ty) in unclaimed:
                    frontier.add((tx, ty))

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax + ay

    # Determine target lists to evaluate quickly
    targets = []
    if frontier:
        targets = list(frontier)
    elif unclaimed:
        # limit for speed/determinism
        targets = sorted(unclaimed, key=lambda p: (man(p[0], p[1], w - 1, h - 1), p[0], p[1]))[:18]
    elif opp_terr:
        targets = sorted(opp_terr, key=lambda p: (man(p[0], p[1], sx, sy), p[0], p[1]))[:12]
    else:
        return [0, 0]

    # Evaluate candidate move by best heuristic to closest target and immediate ownership effect
    best = None
    for dx, dy, nx, ny in candidates:
        immediate = 0
        if (nx, ny) in self_terr:
            immediate += 2
        if (nx, ny) in unclaimed:
            immediate += 4
        if (nx, ny) in opp_terr:
            immediate += 7 if aggressive else -1

        # Encourage moving toward target while avoiding opponent territory when not aggressive
        best_to_target = 10**9
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            if d < best_to_target:
                best_to_target = d
        # Slight preference for central area to reduce wall hits/obstacles
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = abs(nx - cx) + abs(ny - cy)

        score = immediate * 10 - best_to_target - int(center_pen)
        # Deterministic tie-breaker: prefer smaller dx,dy ordering based on move list
        idx = moves.index((dx, dy)) if (dx, dy) in moves else 0
        key = (score, -immediate, -idx, nx, ny)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]