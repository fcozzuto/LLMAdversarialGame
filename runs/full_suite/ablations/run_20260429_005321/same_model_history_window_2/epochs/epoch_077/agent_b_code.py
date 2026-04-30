def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a target resource: minimize our distance, tie-break by maximizing distance from opponent.
    if resources:
        target = resources[0]
        best_key = None
        for r in resources:
            rx, ry = r
            k1 = cheb(sx, sy, rx, ry)
            k2 = -cheb(ox, oy, rx, ry)
            k = (k1, k2, rx, ry)
            if best_key is None or k < best_key:
                best_key = k
                target = r
        tx, ty = target
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = -10**18

    alpha = 0.35  # opponent pressure weight

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            dmin = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            dopp = cheb(nx, ny, ox, oy)
            dtx = cheb(nx, ny, tx, ty)
            # Prefer getting closer to the chosen target, and keeping opponent farther from us.
            score = (-dmin) + 0.9 * (-dtx) - alpha * dopp
        else:
            score = -cheb(nx, ny, ox, oy)
        # deterministic tie-break: lexicographic on (score, dx, dy) with fixed dir order already
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]