def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    obstacles.discard((sx, sy))
    obstacles.discard((ox, oy))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # If already on a resource, stay to guarantee capture.
    res_set = set(resources)
    if (sx, sy) in res_set:
        return [0, 0]

    # Choose target resource where we gain tempo over opponent.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we are closer to; if tie, prefer farther from opponent.
        key = (do - ds, -ds, ry, rx)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, None, None, None)  # score, nds, ndo, idx

    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # Main: minimize self distance to target; Secondary: maximize opponent distance to that target.
        # Tertiary: avoid oscillation by slight preference for smaller step magnitude.
        step_mag = abs(dx) + abs(dy)
        score = (-nds, ndo, -step_mag, i)
        if best_move[0] is None or score > best_move[0]:
            best_move = (score, dx, dy, i)

    if best_move[1] is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]