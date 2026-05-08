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

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    candidates = list(unclaimed)
    if not candidates:
        candidates = list(oppT)

    if not candidates:
        return [0, 0]

    # Deterministic target selection: prefer nearer-to-self, farther-from-opponent, and towards edges
    best = None
    best_val = None
    for tx, ty in sorted(candidates):
        if (tx, ty) in obstacles:
            continue
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        edge = (tx in (0, w - 1) or ty in (0, h - 1)) * 0.15
        center_pen = (abs(tx - cx) + abs(ty - cy)) * 0.03
        # If target is already ours, still allow move if nothing else exists
        # We want to reach fast while keeping opponent away
        val = ds - 0.45 * do - edge + center_pen
        if best is None or val < best_val:
            best, best_val = (tx, ty), val

    tx, ty = best
    # Move selection among 9 options: avoid obstacles; prefer reducing distance to target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestmv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d1 = man(nx, ny, tx, ty)
        d0 = man(sx, sy, tx, ty)
        # Small tie-break: prefer moves that increase our control chances (towards unclaimed, away from opponent)
        flip_bonus = 0.0
        if (nx, ny) in oppT:
            flip_bonus = 0.18
        edge = (nx in (0, w - 1) or ny in (0, h - 1)) * 0.05
        toward_opp = man(nx, ny, ox, oy) - man(sx, sy, ox, oy)
        val = d1 + (0 if d1 < d0 else 0.08) - flip_bonus - edge + 0.02 * toward_opp
        if bestmv is None or val < bestmv or (val == bestmv and (dx, dy) < bestm):
            bestmv, bestm = val, (dx, dy)

    return [int(bestm[0]), int(bestm[1])]