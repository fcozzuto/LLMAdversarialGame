def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = -10**18

    # Deterministic: pick move with max score; ties broken by move order (dirs).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Base: avoid stepping toward opponent if nothing else is attractive.
        base = 0.0
        dist_opp = cheb(nx, ny, ox, oy)
        base += 0.08 * dist_opp

        if resources:
            # Choose best resource outcome from this next position.
            best_here = -10**18
            for rx, ry in resources:
                d_us = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # Prefer resources we can reach sooner than opponent; otherwise contest less.
                win_factor = (d_op - d_us)
                # Encourage getting closer fast; slight penalty for larger distances overall.
                score = 2.2 * win_factor - 0.35 * d_us
                # If opponent is also very close to the resource, reduce commitment.
                score -= 0.12 * max(0, 4 - d_op)
                # Prefer nearer to center only as a weak tie-breaker.
                score -= 0.02 * (abs(nx - cx) + abs(ny - cy))
                if score > best_here:
                    best_here = score
            score_total = base + best_here
        else:
            # No visible resources: drift toward center while keeping distance from opponent.
            score_total = base - 0.05 * (abs(nx - cx) + abs(ny - cy))
        if score_total > best_score:
            best_score = score_total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]