def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Prefer moves that are hard to approach, assume opponent moves to minimize distance to us.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    target_corner_bias = 0.15 if observation.get("turn_index", 0) % 2 == 0 else 0.05

    best = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Opponent response: choose move that minimizes our distance after it moves.
        min_dist = None
        for odx, ody in dirs:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            d = cheb(nx, ny, tx, ty)
            if min_dist is None or d < min_dist:
                min_dist = d

        if min_dist is None:
            continue

        # Tie-break: go toward farthest corner if it's still safe.
        corner_d = cheb(nx, ny, far_corner[0], far_corner[1])
        # Higher is better; corner_d smaller is closer, so subtract.
        score = min_dist - target_corner_bias * corner_d

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break: prefer staying still, then axis-aligned, then lower dx, then lower dy.
            if best == (0, 0) and (dx, dy) != (0, 0):
                continue
            if best != (0, 0) and (dx, dy) == (0, 0):
                best = (dx, dy)
                continue
            def key(m):
                m2x, m2y = m
                axis = 0 if (m2x == 0 or m2y == 0) else 1
                return (axis, m2x, m2y)
            if key((dx, dy)) < key(best):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]