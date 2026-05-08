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
    if not unclaimed and resources:
        unclaimed = set(resources)

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not unclaimed:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_cell = None
    best_val = -10**18
    for tx, ty in unclaimed:
        if (tx, ty) in obstacles:
            continue
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        dc = abs(tx - cx) + abs(ty - cy)
        # Prefer nearby claims that are far from opponent and not too cornered.
        val = (-ds) + 0.6 * do - 0.08 * dc
        if val > best_val:
            best_val = val
            best_cell = (tx, ty)

    tx, ty = best_cell
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Local move quality: capture/expand more valuable than being closer to center.
        score = 0.0
        if (nx, ny) in unclaimed:
            score += 6.0
        if (nx, ny) in oppT:
            score += 7.0  # flipping opponent territory on entry
        if (nx, ny) in selfT:
            score += 1.5
        score += 2.0 / (1 + md(nx, ny, tx, ty))  # move toward target
        score += 0.2 * md(nx, ny, ox, oy)          # keep away from edge claimer pressure
        # Small bias: avoid stepping into opponent-owned unless it's also the target direction.
        if (nx, ny) in oppT and (tx, ty) not in oppT:
            score -= 0.4
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]