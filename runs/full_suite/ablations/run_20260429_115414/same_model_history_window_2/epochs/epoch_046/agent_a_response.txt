def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            cand = (-d, dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[1], best[2]] if best is not None else [0, 0]

    # Choose move that maximizes "catch potential": prefer moving toward resources where we beat opponent,
    # and among those, pick the one with largest advantage; add small tie-break toward nearer resources.
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Avoid stepping away if it makes us worse everywhere.
        worst_local = 10**9
        best_local = -10**9

        for rx, ry in resources:
            ds_now = cheb(sx, sy, rx, ry)
            do_now = cheb(ox, oy, rx, ry)
            ds_next = cheb(nx, ny, rx, ry)
            do_next = cheb(ox, oy, rx, ry)

            # Advantage positive means we are closer than opponent (or become closer).
            adv_now = do_now - ds_now
            adv_next = do_next - ds_next

            # If we can pick this resource sooner than opponent, prioritize; otherwise still move toward nearest.
            pick_bias = 0
            if (nx, ny) == (rx, ry):
                pick_bias = 1000
            cand = pick_bias + (adv_next * 40) + (adv_next - adv_now) * 10 - ds_next
            if cand < worst_local:
                worst_local = cand
            if cand > best_local:
                best_local = cand

        # Penalize moves that don't improve our best opportunity.
        # Also prefer staying valid (already) and slight centrality to avoid getting trapped near edges.
        center_pen = cheb(nx, ny, cx, cy)
        score = best_local - 0.05 * center_pen + 0.01 * worst_local
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]