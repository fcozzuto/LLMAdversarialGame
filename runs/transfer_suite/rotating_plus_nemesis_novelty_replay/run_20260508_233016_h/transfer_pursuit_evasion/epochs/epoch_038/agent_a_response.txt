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

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Opponent response: choose move that maximizes our distance (zigzag-like evasion)
        best_op = None
        best_op_dist = None
        for odx, ody in dirs:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            dist = cheb(nx, ny, tx, ty)
            if best_op_dist is None or dist > best_op_dist:
                best_op_dist = dist
                best_op = (tx, ty)
        if best_op is None:
            best_op = (ox, oy)

        # Score our move: minimize resulting distance, add slight tie-break for reducing opponent mobility
        mx, my = best_op
        opp_moves = 0
        for odx, ody in dirs:
            tx, ty = mx + odx, my + ody
            if valid(tx, ty):
                opp_moves += 1
        val = (best_op_dist, -opp_moves)

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]