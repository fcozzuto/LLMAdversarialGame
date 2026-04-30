def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def dist_cheb(ax, ay, bx, by):
        dx, dy = abs(ax - bx), abs(ay - by)
        return dx if dx > dy else dy

    def step_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Target selection: prefer resource with positive advantage; otherwise least-bad.
    if resources:
        best = None
        best_score = None
        for tx, ty in resources:
            ds = dist_cheb(sx, sy, tx, ty)
            do = dist_cheb(ox, oy, tx, ty)
            adv = do - ds
            # Tie-break toward closer to us, then lexicographic.
            key = (-(adv), ds, tx, ty)
            if best is None or key < best_score:
                best = (tx, ty)
                best_score = key
        tx, ty = best
    else:
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)

    # Move choice: go toward target, but strongly avoid blocking itself and being trapped near obstacles.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue

        # Primary: reduce chebyshev distance to target.
        cur = dist_cheb(sx, sy, tx, ty)
        nxt = dist_cheb(nx, ny, tx, ty)
        val = (cur - nxt) * 100

        # Secondary: deny opponent progress to same target.
        opp_cur = dist_cheb(ox, oy, tx, ty)
        opp_nxt = dist_cheb(ox, oy, tx, ty)  # opponent moves next; we can't predict, but keep comparative pressure small
        val += (opp_cur - opp_nxt) * 0

        # Tertiary: obstacle pressure heuristic (prefer squares with more free neighbors).
        free = 0
        for ddx, ddy in dirs:
            ex, ey = nx + ddx, ny + ddy
            if step_ok(ex, ey):
                free += 1
        val += free

        # Deterministic tie-break.
        key = (-val, dx, dy, nx, ny)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]