def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unclaimed_set.add((int(p[0]), int(p[1])))

    self_terr = observation.get("self_territory") or []
    self_terr_set = set()
    for p in self_terr:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_terr_set.add((int(p[0]), int(p[1])))

    opp_terr = observation.get("opponent_territory") or []
    opp_terr_set = set()
    for p in opp_terr:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_terr_set.add((int(p[0]), int(p[1])))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # pick a deterministic "frontier" direction: nearest unclaimed to our territory; else to us
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    if self_terr_set and unclaimed_set:
        best = None
        for ut in unclaimed_set:
            d = min(man(ut, st) for st in self_terr_set)  # small sets typical; deterministic
            cand = (d, man(ut, (sx, sy)), ut[0], ut[1])
            if best is None or cand < best:
                best = cand
        target = (best[2], best[3]) if best else None
    if target is None and unclaimed_set:
        target = min(unclaimed_set, key=lambda t: (man(t, (sx, sy)), t[0], t[1]))
    if target is None:
        target = (cx, cy)

    best_move = (0, 0)
    best_score = -10**18

    # Move scoring: strongly prefer entering unclaimed, then approaching target; slight bias against obstacles
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed_set:
            score += 100000
        if (nx, ny) in opp_terr_set:
            score += 2500 - 2 * man((nx, ny), target)
        if (nx, ny) in self_terr_set:
            score += 200
        # approach target
        score += -20 * man((nx, ny), target)
        # keep moving generally toward center if no unclaimed
        score += -3 * man((nx, ny), (cx, cy))
        # discourage staying unless it's already best/forced
        if dx == 0 and dy == 0:
            score -= 5

        # deterministic tie-break: prefer lexicographically smallest move among equals
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]