def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = 0 if sx > ox else w - 1
        ty = 0 if sy > oy else h - 1
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = -cheb(nx, ny, tx, ty)
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Score moves by the best resource we can "claim" relative to opponent.
    # Prefer resources where we are closer (or can become closer next).
    best_val = -10**18
    best_move = [0, 0]
    # Stable tie-break preference: move order already deterministic.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        move_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we can reach before/at opponent, strongly prefer.
            # If opponent is closer, still consider but penalize heavily.
            diff = do - ds
            val = 0
            if diff >= 0:
                val = 200 - ds * 3 + diff * 10
            else:
                val = 50 - ds * 2 + diff * 12  # diff is negative
            # Mild preference for mid-late game: when fewer resources remain, commit.
            rr = observation.get("remaining_resource_count")
            if rr is None:
                rr = 0
            try:
                rr = int(rr)
            except Exception:
                rr = 0
            val += (12 - rr) * (1 if diff >= 0 else -0.5)
            if val > move_best:
                move_best = val
        if move_best > best_val:
            best_val = move_best
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]