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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    rem = observation.get("remaining_resource_count")
    try:
        rem = int(rem or 0)
    except:
        rem = 0
    late = rem <= 3

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources I can reach earlier; late-game prefer smaller absolute distance
            score = (opd - myd) * 10 - myd
            if late:
                score += -myd // 2
            # Small tie-break towards upper-left-ish to break symmetry deterministically
            score += -(rx + ry) * 0.01
            if best is None or score > best[0]:
                best = (score, rx, ry)
        target = (best[1], best[2])

    if target is None:
        # Deterministic fallback: move towards center
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)

        # Mild opponent avoidance to prevent easy contest swings
        d_to_o = cheb(nx, ny, ox, oy)
        avoid = -3 if d_to_o == 0 else 0
        # If late, allow closer to opponent; otherwise keep some spacing
        spacing_pen = (2 if not late else 0) * (1 if d_to_o <= 1 else 0)

        # Deterministic tie-break: prefer moves with smaller dx, then smaller dy
        tie = abs(dx) * 10 + abs(dy)
        val = d_to_t + spacing_pen + avoid + tie * 0.0001
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]