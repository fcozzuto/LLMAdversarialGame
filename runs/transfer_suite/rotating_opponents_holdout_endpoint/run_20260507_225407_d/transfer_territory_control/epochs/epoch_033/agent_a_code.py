def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    un = to_set("unclaimed_cells")

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    # Deterministic target: prefer frontier-ish unclaimed cells near us and near opponent.
    tx, ty = sx, sy
    best = None
    if un:
        for x, y in un:
            ds = man(x, y, sx, sy)
            do = man(x, y, ox, oy)
            # Lower is better.
            score = ds - 0.75 * do + 0.01 * (x * 8 + y)
            if best is None or score < best[0]:
                best = (score, x, y)
    else:
        # If no unclaimed, push into opponent territory if possible; else just expand ours.
        candidates = list(opp_t) if opp_t else list(self_t)
        for x, y in candidates:
            ds = man(x, y, sx, sy)
            score = ds + 0.001 * (x * 8 + y)
            if best is None or score < best[0]:
                best = (score, x, y)
    if best is not None:
        tx, ty = best[1], best[2]

    # Choose move by 1-step look scoring.
    order = {(-1, -1): 0, (-1, 0): 1, (-1, 1): 2, (0, -1): 3, (0, 0): 4, (0, 1): 5, (1, -1): 6, (1, 0): 7, (1, 1): 8}
    bestm = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue  # avoid obstacle if possible (engine would keep us)
        cell_score = 0.0
        if (nx, ny) in opp_t:
            cell_score -= 5.0
        elif (nx, ny) in un:
            cell_score -= 2.5
        elif (nx, ny) in self_t:
            cell_score += 0.25
        # Main objective: reduce distance to target.
        cell_score += 1.2 * man(nx, ny, tx, ty)
        # Small nudge to move generally toward opponent to gain area/bonuses sooner.
        cell_score += 0.05 * man(nx, ny, ox, oy)
        tie = (cell_score, order.get((dx, dy), 99), nx, ny)
        if bestm is None or tie < bestm[0]:
            bestm = (tie, dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]