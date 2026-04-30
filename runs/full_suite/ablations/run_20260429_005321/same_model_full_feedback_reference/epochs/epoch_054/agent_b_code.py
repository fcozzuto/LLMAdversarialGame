def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - 0.01 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # Competitive targeting: prefer resources where we can arrive earlier than opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        move_val = -10**18
        for rx, ry in resources:
            tself = cheb(nx, ny, rx, ry)
            top = cheb(ox, oy, rx, ry)
            # If we arrive earlier, value increases; closeness also matters.
            # Small opponent-distance tie-break encourages not running away blindly.
            v = 20 * (top - tself) - tself - 0.02 * cheb(nx, ny, ox, oy)
            if v > move_val:
                move_val = v
        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    # Deterministic fallback
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]