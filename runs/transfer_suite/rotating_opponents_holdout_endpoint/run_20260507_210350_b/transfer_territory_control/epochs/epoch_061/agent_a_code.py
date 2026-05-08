def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_t.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = resources if resources else (unclaimed if unclaimed else list(opp_t))
    if not targets:
        return [0, 0]

    best = None
    best_score = -10**9
    # Deterministic tie-break: fixed move order
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            cell = (nx, ny)
            score = 0.0

            if cell in opp_t:
                score += 8.0
            elif cell in unclaimed:
                score += 5.0
            elif cell in self_t:
                score += 3.0

            # Pull toward nearest target
            d = 10**9
            for t in targets:
                dd = dist(cell, t)
                if dd < d:
                    d = dd
            score += max(0.0, 6.0 - 0.8 * d)

            # Mildly avoid letting opponent get closer to our territory frontier:
            # encourage moves that keep distance to opponent increasing slightly
            score += 0.05 * (dist((sx, sy), (ox, oy)) - dist(cell, (ox, oy)))

            if score > best_score:
                best_score = score
                best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]