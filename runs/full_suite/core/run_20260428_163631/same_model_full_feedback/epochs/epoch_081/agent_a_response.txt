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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        tx, ty = cx, cy
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if myd == 0:
                score = 1e9
            else:
                # Prefer resources where we are closer than opponent; also bias toward staying central.
                # Larger is better.
                score = (od - myd) * 100 - myd * 3 - cheb(rx, ry, cx, cy)
            # Deterministic tie-break: lexicographic target
            key = (-score, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # Choose move that best reduces distance to target; penalize walking into opponent-advantaged proximity.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        # If we are at target, just stay (deterministic among equally good moves).
        oppd2 = cheb(ox, oy, tx, ty)
        # Move value: prioritize distance reduction; slight preference toward moves that reduce opponent's ability (indirectly).
        val = (myd2 * 1000) + abs(cheb(nx, ny, ox, oy)) * 2 + oppd2
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]