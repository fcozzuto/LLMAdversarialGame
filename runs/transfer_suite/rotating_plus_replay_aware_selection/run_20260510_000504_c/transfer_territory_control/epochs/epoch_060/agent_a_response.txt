def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def adj8(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    def borders_opponent(cell):
        x, y = cell
        for nx, ny in adj8(x, y):
            if (nx, ny) in opp_terr:
                return True
        return False

    def on_frontier(cell):
        x, y = cell
        for nx, ny in adj8(x, y):
            if (nx, ny) in self_terr:
                return True
        return False

    # Deterministic target: frontier unclaimed that also borders opponent; else best border-opponent cell; else fallback.
    frontier = [c for c in unclaimed if on_frontier(c)]
    if frontier:
        candidates = frontier
    else:
        candidates = list(unclaimed) if unclaimed else []

    if candidates:
        # Prefer immediate contest: unclaimed bordering opponent territory, then closeness to us.
        best = None
        for tx, ty in candidates:
            bo = 1 if borders_opponent((tx, ty)) else 0
            score = (-bo, manhattan(sx, sy, tx, ty), ty, tx)  # smaller is better
            if best is None or score < best[0]:
                best = (score, tx, ty)
        tx, ty = best[1], best[2]
    else:
        # No unclaimed: head to nearest opponent territory cell (likely to flip/expand).
        if opp_terr:
            best = None
            for tx, ty in opp_terr:
                score = (manhattan(sx, sy, tx, ty), ty, tx)
                if best is None or score < best[0]:
                    best = (score, tx, ty)
            tx, ty = best[1], best[2]
        else:
            tx, ty = w - 1, h - 1

    # Choose move that reduces distance to target, with obstacle avoidance and deterministic tie-break.
    best_mv = (None, None, None)  # (dist, tx_rank, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = manhattan(nx, ny, tx, ty)
        # Tie-break to be deterministic and slightly "edge/forward" biased (lower y, then x).
        tieb = (ny, nx)
        cand = (d, tieb[0], tieb[1], dx, dy)
        if best_mv[0] is None or cand < best_mv:
            best_mv = cand
    if best_mv[0] is None:
        return [0, 0]
    return [int(best_mv[3]), int(best_mv[4])]