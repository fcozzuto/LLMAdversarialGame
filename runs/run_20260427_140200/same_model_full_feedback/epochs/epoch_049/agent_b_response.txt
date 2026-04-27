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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_dist(x, y):
        if not resources:
            return cheb(x, y, (w - 1) // 2, (h - 1) // 2)
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    # Deterministic tie-breakers: prefer moves in dirs order; then smaller dx/dy lexicographically.
    best_score = None
    best_move = [0, 0]
    cx, cy = (w - 1) // 2, (h - 1) // 2
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = nearest_dist(nx, ny)
        d_opp = nearest_dist(ox, oy)  # baseline (fixed this turn, deterministic)
        d_opp_after = nearest_dist(ox - 0, oy - 0)  # keep deterministic without predicting
        # Heuristic: go closer to resources; also avoid moves that bring you closer to opponent by chasing same region.
        center_pen = cheb(nx, ny, cx, cy)
        # Combine: minimize (d_self, -progress_capture_bias, center_pen). capture bias encourages moving toward resources.
        progress_bias = 0
        if resources:
            # nearest resource coordinate to approximate "directional" conflict
            tr = resources[0]
            td = cheb(nx, ny, tr[0], tr[1])
            for rx, ry in resources[1:]:
                dd = cheb(nx, ny, rx, ry)
                if dd < td:
                    td, tr = dd, (rx, ry)
            # prefer stepping closer to that chosen target vs staying
            progress_bias = cheb(sx, sy, tr[0], tr[1]) - td

        # Score tuple for lexicographic min
        score = (d_self, -progress_bias, center_pen, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]