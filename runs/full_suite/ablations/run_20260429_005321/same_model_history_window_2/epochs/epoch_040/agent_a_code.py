def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = w // 2, h // 2

    # Target selection: be first on a resource, then stay efficient, then deny opponent access.
    tx, ty = cx, cy
    if resources:
        best_score = -10**18
        best = resources[0]
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer: opponent further by margin, then closer for me, then closer to center to reduce wandering.
            score = (d_op - d_me) * 1000 - d_me * 10 - cheb(rx, ry, cx, cy)
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best

    # Choose next step that minimizes my distance to target, with tie-breaks for safety and keeping pressure.
    best_move = (0, 0)
    best_tuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me_next = cheb(nx, ny, tx, ty)
        d_op_next = cheb(ox, oy, tx, ty)
        deny = d_op_next - d_me_next
        center = cheb(nx, ny, cx, cy)
        # Tuple: higher deny, then smaller distance, then closer to center, then prefer staying still last.
        tup = (-deny, d_me_next, center, abs(dx) + abs(dy))
        if best_tuple is None or tup < best_tuple:
            best_tuple = tup
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]