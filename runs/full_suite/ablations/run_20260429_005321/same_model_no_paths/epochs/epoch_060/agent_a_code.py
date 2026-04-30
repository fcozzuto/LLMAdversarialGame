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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obst_pen(x, y):
        pen = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in obstacles:
                    pen += 1
        return pen

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick target resource where we are relatively closer than opponent, with penalties near obstacles.
    best = None
    best_score = -10**9
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # If we are closer, score higher. If opponent is closer, score lower.
        score = (d_op - d_me) * 3 - adj_obst_pen(rx, ry) - (adj_obst_pen(sx, sy) // 2)
        # Slight deterministic tie-break: prefer smaller (rx,ry).
        score += -0.001 * (rx * 9 + ry)
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_h = 10**9
    # Choose the step that reduces our distance to target while keeping away from obstacles and not stepping into opponent's "pressure".
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        h = cheb(nx, ny, tx, ty)
        h += adj_obst_pen(nx, ny) * 2
        # Avoid moving into squares that are very close to opponent (helps contesting).
        h += max(0, 2 - cheb(nx, ny, ox, oy))
        if h < best_h or (h == best_h and (dx, dy) < best_m):
            best_h = h
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]