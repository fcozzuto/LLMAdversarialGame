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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # drift away from opponent while moving toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            myc = cheb(nx, ny, cx, cy)
            opc = cheb(nx, ny, ox, oy)
            val = myc - 0.2 * opc
            if val < best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Choose target resource where we are relatively closer than opponent.
    best_t = None
    best_rel = 10**18
    # deterministically prefer certain targets via lex tie-break
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        rel = md - od
        if rel < best_rel or (rel == best_rel and (rx, ry) < best_t):
            best_rel = rel
            best_t = (rx, ry)

    rx, ry = best_t

    # Evaluate candidate moves: move closer to our chosen target, while not helping opponent.
    # Also lightly avoid cells adjacent to obstacles.
    def obstacle_adj_score(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    return 1
        return 0

    best = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(nx, ny, ox, oy)
        opp_target_after = cheb(ox, oy, rx, ry)
        # Our progress minus how much we reduce opponent's relative situation
        # (using opponent-target distance as baseline keeps it stable/deterministic)
        val = myd - 0.6 * opp_target_after + 0.2 * (opd) + 0.8 * obstacle_adj_score(nx, ny)
        # Tie-break: prefer diagonal, then toward lower dx/dy ordering in dirs (already deterministic)
        if val < best[0]:
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]