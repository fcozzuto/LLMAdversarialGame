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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_move = (0, 0)
        best_score = None
        # Greedy: choose the move that maximizes our lead over the opponent
        # for the best resource after that move.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Evaluate best resource lead from this hypothetical position.
            # Lead is positive when we are closer (in Chebyshev distance).
            lead_best = -10**9
            tie = 0
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                lead = d_op - d_me
                if lead > lead_best:
                    lead_best = lead
                    tie = 0
                elif lead == lead_best:
                    # Deterministic tie-break: prefer smaller of our distance, then resource index.
                    if d_me < tie:
                        tie = d_me
            # Secondary: prefer reducing our distance to the currently best resource lead.
            # (Approximate by looking at the nearest resource from nx,ny.)
            d_near = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < d_near:
                    d_near = d
            score = (lead_best, -d_near)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: drift deterministically toward center to be ready.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    bestd = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, cx, cy)
        if bestd is None or d < bestd or (d == bestd and (dx, dy) < best):
            bestd = d
            best = (dx, dy)
    return [best[0], best[1]]