def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_move(nx, ny):
        if (nx, ny) == (sx, sy):
            stay_pen = 1
        else:
            stay_pen = 0

        # Choose a "best" resource for this move; deterministic: fixed ordering by resource list.
        best = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can get before opponent, but allow contest blocks by reducing opponent lead.
            # Lower distance is better, being closer than opponent is strongly better.
            rel = do - ds  # positive means we are closer than opponent
            if rel >= 1:
                val = 1000 + 40 * rel - 5 * ds
            else:
                # If opponent leads, try to reduce their advantage.
                val = 50 + 10 * rel - 3 * ds + 2 * (do - cheb(sx, sy, rx, ry))
            # Small preference to not chase far behind when resources are many.
            val -= 0.01 * (ds + do)
            if val > best:
                best = val
        if not resources:
            # No resources: go toward center while staying safe.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            best = -cheb(nx, ny, cx, cy)
        return best - 0.5 * stay_pen

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = score_move(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = v
            best_move = [dx, dy]
    return best_move