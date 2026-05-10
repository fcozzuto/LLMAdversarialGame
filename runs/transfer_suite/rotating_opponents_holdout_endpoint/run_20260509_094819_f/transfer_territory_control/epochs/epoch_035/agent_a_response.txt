def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    myT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    myc = int(observation.get("self_territory_count", len(myT)))
    oppc = int(observation.get("opponent_territory_count", len(oppT)))
    behind = 1 if myc < oppc else 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_d2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    targets = None
    if behind:
        targets = [p for p in oppT] if oppT else list(uncla)
    else:
        targets = list(uncla) if uncla else list(oppT)
    if not targets:
        return [0, 0]

    best = None
    # pick one deterministic "best" target by minimal distance, then lexicographic
    for tx, ty in targets:
        if not inb(tx, ty):
            continue
        v = cell_d2(sx, sy, tx, ty)
        cand = (v, tx, ty)
        if best is None or cand < best:
            best = cand
            best_t = (tx, ty)
    tx, ty = best_t

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        score = cell_d2(nx, ny, tx, ty)
        # bias toward capturing: entering opponent territory is valuable
        if (nx, ny) in oppT:
            score -= 30
        if (nx, ny) in uncla:
            score -= 6
        # slight bias to avoid getting stuck at edges
        if dx == 0 and dy == 0:
            score += 2
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]