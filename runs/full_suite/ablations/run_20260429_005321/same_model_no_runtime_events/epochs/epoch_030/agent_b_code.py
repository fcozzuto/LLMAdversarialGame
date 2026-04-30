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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        ax = ax - bx
        if ax < 0: ax = -ax
        ay = ay - by
        if ay < 0: ay = -ay
        return ax + ay

    def score_cell(x, y):
        # Prefer cells where I am relatively closer to a resource than the opponent.
        best = -10**9
        for rx, ry in resources:
            myd = md(x, y, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Higher is better: win the race to resources; slight preference for nearer resources overall.
            s = (opd - myd) * 10 - myd
            if s > best:
                best = s
        if not resources:
            # Default to center-ish to keep options open.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            best = -md(x, y, cx, cy)
        return best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Tie-break deterministically by a fixed move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        val = score_cell(nx, ny)
        # Small additional preference to keep progressing toward the best resource distance gradient.
        if resources:
            # Evaluate immediate distance reduction to my best target.
            cur_best = 10**9
            nxt_best = 10**9
            for rx, ry in resources:
                cur_best = min(cur_best, md(sx, sy, rx, ry))
                nxt_best = min(nxt_best, md(nx, ny, rx, ry))
            val += (cur_best - nxt_best) * 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]