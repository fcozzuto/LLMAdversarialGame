def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Niche shift: prioritize "row-disjoint" resources to counter row-sweeping opponents.
    best = None
    best_val = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        row_pen = -50 if ry == oy else 0
        row_bonus = abs(ry - oy)
        adv = do - ds  # higher means we are closer
        # Maximize: avoid opponent's current row sweep, then win races on closeness.
        val = row_pen + row_bonus * 2.0 + adv * 1.5 - ds * 0.25
        if best is None or val > best_val or (val == best_val and (ds, rx, ry) < best):
            best, best_val = (ds, rx, ry), val

    if best is None:
        return [0, 0]
    tx, ty = best[1], best[2]

    def sign(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    # Try candidate moves; filter obstacle targets; deterministic tie-breaking.
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates.sort()

    bx, by = sign(tx - sx), sign(ty - sy)
    # Prefer moves that also reduce opponent row access (keep stepping away if target is on opponent row).
    prefer_row_disjoint = (ty == oy)

    best_move = [0, 0]
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        race = (do2 - ds2)
        row_after = ny == oy
        row_term = -8 if (prefer_row_disjoint and row_after) else (2 if (not prefer_row_disjoint and not row_after) else 0)
        align = -(abs(dx - bx) + abs(dy - by)) * 0.1
        score = race * 2.0 - ds2 * 0.35 + row_term + align
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]