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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    if not resources:
        # Deterministic fallback: drift toward center while keeping safe.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            score = cheb(int(nx), int(ny), int(cx), int(cy))
            if best is None or score < best[0] or (score == best[0] and (nx, ny) < best[1]):
                best = (score, (nx, ny), dx, dy)
        return [best[2], best[3]]

    # Choose our target: nearest resource by Chebyshev, tie by (x,y).
    best_r = None
    for x, y in resources:
        d = cheb(sx, sy, x, y)
        if best_r is None or d < best_r[0] or (d == best_r[0] and (x, y) < best_r[1]):
            best_r = (d, (x, y))
    tx, ty = best_r[1]

    # Also find opponent's nearest resource for a simple contest heuristic.
    best_ro = None
    for x, y in resources:
        d = cheb(ox, oy, x, y)
        if best_ro is None or d < best_ro[0] or (d == best_ro[0] and (x, y) < best_ro[1]):
            best_ro = (d, (x, y))
    otx, oty = best_ro[1]

    # Pick move that minimizes our distance to our target, while discouraging giving opponent closer access.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_us = cheb(nx, ny, tx, ty)
        d_op_to_our = cheb(ox, oy, tx, ty)
        d_op_after = cheb(ox, oy, otx, oty)

        # Immediate contest value: if we move closer to our target, increase relative gain; also reduce opponent advantage.
        # Deterministic: add tiny tie-break by position.
        score = d_us * 1000 - (d_op_to_our - d_op_after) * 10 + (abs(nx - ox) + abs(ny - oy))
        pos = (nx, ny)
        if best is None or score < best[0] or (score == best[0] and pos < best[1]):
            best = (score, pos, dx, dy)

    return [best[2], best[3]]