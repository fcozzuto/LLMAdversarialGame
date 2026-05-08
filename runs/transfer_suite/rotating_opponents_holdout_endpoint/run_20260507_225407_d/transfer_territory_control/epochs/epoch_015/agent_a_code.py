def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        obstacles.add((int(p[0]), int(p[1])))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    resources = set((int(p[0]), int(p[1])) for p in (observation.get("resources") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    def val(x, y):
        if (x, y) in obstacles:
            return -10**9
        # Strongly prioritize flipping opponent territory
        if (x, y) in opp_terr:
            return 1200 - 0.35 * manh(x, y)
        if (x, y) in resources:
            return 1100 - 0.25 * manh(x, y)
        if (x, y) in unclaimed:
            return 520 - 0.15 * manh(x, y)
        if (x, y) in self_terr:
            return 160 - 0.05 * manh(x, y)
        return 220 - 0.08 * manh(x, y)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    # Deterministic 2-step lookahead: score = immediate + 0.7*next + small anti-stall term
    stall_pen = 6 if observation.get("self_position") == observation.get("self_position") else 0  # always 6
    for dx, dy in dirs:
        x1, y1 = sx + dx, sy + dy
        if not inb(x1, y1) or (x1, y1) in obstacles:
            continue
        s1 = val(x1, y1)
        score = s1
        if not (dx == 0 and dy == 0):
            score -= 2  # slight preference to keep moving

        # Second step
        local_best = -10**18
        for dx2, dy2 in dirs:
            x2, y2 = x1 + dx2, y1 + dy2
            if not inb(x2, y2) or (x2, y2) in obstacles:
                continue
            local_best = max(local_best, val(x2, y2))
        if local_best == -10**18:
            local_best = 0
        score += 0.7 * local_best

        # Prefer moving to cells that reduce distance to opponent territory centroid if visible
        if opp_terr:
            cx = sum(x for x, _ in opp_terr) / len(opp_terr)
            cy = sum(y for _, y in opp_terr) / len(opp_terr)
            score -= 0.03 * (abs(x1 - cx) + abs(y1 - cy))

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]