def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            key = (cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return list(best if best is not None else (0, 0))

    best_move = (0, 0)
    best_val = -10**18
    best_tie = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate best target resource for this move: favor (opponent_far - my_close)
        # Also penalize moves that bring us closer to the opponent when we're not much closer to resources.
        best_local = -10**18
        best_res = None
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = (od - md) - 0.15 * cheb(nx, ny, ox, oy)
            if val > best_local or (val == best_local and (rx, ry) < best_res):
                best_local, best_res = val, (rx, ry)

        md_best = cheb(nx, ny, best_res[0], best_res[1])
        od_best = cheb(ox, oy, best_res[0], best_res[1])
        # Tie-break: prefer smaller my distance, then larger opponent distance, then stable ordering.
        tie = (-(od_best - md_best), md_best, dx, dy)
        if best_local > best_val or (best_local == best_val and (tie < best_tie if best_tie is not None else True)):
            best_val, best_tie, best_move = best_local, tie, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]