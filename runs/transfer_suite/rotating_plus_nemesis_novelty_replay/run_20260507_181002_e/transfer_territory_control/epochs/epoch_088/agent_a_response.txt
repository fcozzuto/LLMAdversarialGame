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
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    bestv = -10**9
    # Prefer: (1) counterclaim opponent territory when close; (2) otherwise expand into unclaimed far from opponent.
    # Deterministic tie-break by fixed move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        is_unclaimed = (nx, ny) in unclaimed
        is_opp = (nx, ny) in oppT
        is_self = (nx, ny) in selfT
        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_cur = abs(sx - ox) + abs(sy - oy)
        v = 0
        v += 3 if is_unclaimed else 0
        if is_opp:
            v += 9 + dist_opp  # flip pressure, slightly favor farther landing to avoid being surrounded
        if is_self:
            v -= 1  # discourage stagnation
        v += (dist_opp - dist_cur)  # prefer moving away unless counterclaiming
        # If opponent is adjacent, prioritize taking their territory
        if dist_cur <= 2 and not is_opp:
            v -= 2
        # Avoid stepping next to obstacles too much (local safety)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if inb(x2, y2) and (x2, y2) in obstacles:
                    adj_obs += 1
        v -= adj_obs * 0.5
        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]