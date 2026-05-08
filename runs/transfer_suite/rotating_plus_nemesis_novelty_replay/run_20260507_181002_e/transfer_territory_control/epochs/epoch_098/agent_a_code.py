def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    unclaimed |= resources

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def eval_cell(x, y):
        if (x, y) in obstacles:
            return -10**12
        d = abs(x - ox) + abs(y - oy)
        on_un = (x, y) in unclaimed
        on_self = (x, y) in selfT
        on_opp = (x, y) in oppT

        # Base for controlling more territory
        score = 0
        if on_self:
            score += 2
        if on_un:
            score += 6 + (d / 10.0)  # expand away from opponent
        if on_opp:
            # Prefer counterclaiming only if it helps distance control
            score += 4 + (d / 12.0)
            # discourage walking into opponent area while also getting closer
            score -= (20.0 / (1.0 + d)) if d < abs(sx - ox) + abs(sy - oy) else 0

        # Mild edge preference (safer corridor building)
        edge = (x == 0) or (x == w - 1) or (y == 0) or (y == h - 1)
        if edge:
            score += 0.6

        # Avoid moving directly adjacent to obstacles less than harshly
        # (deterministic but cheap): if any obstacle in 1-step neighborhood, slightly reduce
        near_obs = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    near_obs += 1
        score -= near_obs * 0.2

        return score

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = eval_cell(nx, ny)
        # tie-break deterministically: prefer moves that increase distance, then x, then y
        if v > bestv + 1e-9:
            bestv = v
            best = (dx, dy)
        elif abs(v - bestv) <= 1e-9 and best is not None:
            prevx, prevy = sx + best[0], sy + best[1]
            cand_dist = abs(nx - ox) + abs(ny - oy)
            prev_dist = abs(prevx - ox) + abs(prevy - oy)
            if cand_dist > prev_dist or (cand_dist == prev_dist and (nx, ny) < (prevx, prevy)):
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]