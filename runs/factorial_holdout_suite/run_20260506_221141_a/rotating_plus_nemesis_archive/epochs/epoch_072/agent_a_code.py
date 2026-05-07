def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Immediate capture if adjacent (Chebyshev distance 1)
    best_adj = None
    for rx, ry in resources:
        if cheb(sx, sy, rx, ry) == 1:
            if best_adj is None or (rx, ry) < best_adj:
                best_adj = (rx, ry)
    if best_adj is not None:
        rx, ry = best_adj
        dx = 0 if rx == sx else (1 if rx > sx else -1)
        dy = 0 if ry == sy else (1 if ry > sy else -1)
        if safe(sx + dx, sy + dy):
            return [dx, dy]

    # Choose target: favor resources where we are closer than opponent; if tie, deterministic by coords.
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Lower key is better: lead first, then shorter path; last tie by position.
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    # Candidate moves ordered deterministically; prefer reducing cheb distance to target.
    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        if best_d is None or nd < best_d or (nd == best_d and (dx, dy) < best_move):
            best_d = nd
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]