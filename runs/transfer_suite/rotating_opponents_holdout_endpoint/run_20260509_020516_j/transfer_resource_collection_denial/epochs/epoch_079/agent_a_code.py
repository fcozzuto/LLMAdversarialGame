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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        ax = -dx if dx < 0 else dx
        ay = -dy if dy < 0 else dy
        return ax if ax > ay else ay

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        best_move = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            k = (cheb(nx, ny, (w - 1) // 2, (h - 1) // 2), cheb(nx, ny, ox, oy))
            if best_key is None or k < best_key:
                best_key = k
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Target selection: prefer resources where we beat opponent, but avoid likely "sweep" lines (same row/col as opponent).
    # sweep_rows tends to contest along opponent's row/col; we bias away to keep initiative.
    same_line_pen = 2
    best_target = None
    best_tkey = None
    for (rx, ry) in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        line_pen = same_line_pen if (rx == ox or ry == oy) else 0
        # Also mildly prefer resources farther from opponent to reduce immediate contest.
        tkey = (sd - od + line_pen, sd, od)
        if best_tkey is None or tkey < best_tkey:
            best_tkey = tkey
            best_target = (rx, ry)

    tx, ty = best_target

    # Move scoring: reduce distance to target; if tie, keep away from opponent to prevent steals.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_opp = cheb(nx, ny, ox, oy)
        # Prefer moves that likely reach the target sooner.
        key = (d_to_t, -d_from_opp, (nx, ny))
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]