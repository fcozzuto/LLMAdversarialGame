def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if not resources:
        # Deterministic drift toward center to reduce being stuck
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = d2(nx, ny, tx, ty)
            if sc < best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Choose move that best improves chance to secure a resource vs opponent
    best_move = (10**18, 0, 0)
    # Tie-break resources deterministically: prefer lower x then y
    res_sorted = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if inb(rx, ry) and (rx, ry) not in obstacles:
                res_sorted.append((rx, ry))
    if not res_sorted:
        return [0, 0]
    res_sorted.sort()

    # Precompute opponent distances to resources
    opp_d = {}
    for rx, ry in res_sorted:
        opp_d[(rx, ry)] = d2(ox, oy, rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate best target from this next position
        best_for_move = None
        for rx, ry in res_sorted:
            sd = d2(nx, ny, rx, ry)
            od = opp_d[(rx, ry)]
            # Prefer taking closer resources; heavily penalize targets closer to opponent
            # Lower is better.
            v = sd - 2.2 * od + 0.03 * sd + 0.0001 * (rx + 7 * ry)
            if best_for_move is None or v < best_for_move:
                best_for_move = v
        # Also consider slightly reducing our distance to the currently best resource
        if best_for_move is None:
            continue
        if best_for_move < best_move[0] or (best_for_move == best_move[0] and (dx, dy) < (best_move[1], best_move[2])):
            best_move = (best_for_move, dx, dy)

    return [best_move[1], best_move[2]]