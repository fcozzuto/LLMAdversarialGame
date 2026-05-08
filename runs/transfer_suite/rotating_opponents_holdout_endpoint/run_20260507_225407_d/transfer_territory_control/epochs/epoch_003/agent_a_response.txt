def choose_move(observation):
    sx, sy = observation["self_position"]
    gx, gy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    self_cells = observation.get("self_territory") or []
    opp_cells = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    self_count = observation.get("self_territory_count", len(self_cells))
    opp_count = observation.get("opponent_territory_count", len(opp_cells))
    behind = self_count < opp_count

    opp_set = set((x, y) for x, y in opp_cells)
    self_set = set((x, y) for x, y in self_cells)
    unclaimed_set = set((x, y) for x, y in unclaimed)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target = None
    if behind and opp_set:
        target = min(opp_set, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
    elif unclaimed_set:
        target = min(unclaimed_set, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        target = (gx, gy)

    best = None
    best_score = -10**18
    for dx, dy, nx, ny in candidates:
        score = 0
        if (nx, ny) in opp_set:
            score += 1000000
        elif (nx, ny) in unclaimed_set:
            score += 1000
        elif (nx, ny) in self_set:
            score += 50

        dcur = md(sx, sy, target[0], target[1])
        dnext = md(nx, ny, target[0], target[1])
        score += (dcur - dnext) * 10

        # Prefer progressing generally toward opponent when contesting, otherwise toward target.
        score += max(0, (md(sx, sy, gx, gy) - md(nx, ny, gx, gy))) * (20 if behind else 5)

        # Avoid stepping into "bad" local chokepoints adjacent to many opponent cells.
        adj_opp = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx2, ty2 = nx + ax, ny + ay
                if 0 <= tx2 < w and 0 <= ty2 < h and (tx2, ty2) in opp_set:
                    adj_opp += 1
        score -= adj_opp * (15 if behind else 8)

        # Mild tie-break: deterministic
        score -= (abs(dx) + abs(dy)) * 0.1
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]