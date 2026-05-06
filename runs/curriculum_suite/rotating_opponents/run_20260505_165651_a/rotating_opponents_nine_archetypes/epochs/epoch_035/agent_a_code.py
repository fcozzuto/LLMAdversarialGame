def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # If opponent is very close, prioritize evasion to avoid probes/steals.
    opp_close = king_dist(sx, sy, ox, oy) <= 2

    # Target scoring: pick a resource that's closer to us than to opponent, while still reachable.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        # No resources: head to center while staying away from opponent.
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in valid:
            d_opp = king_dist(nx, ny, ox, oy)
            v = 0.9 * d_opp - 0.05 * king_dist(nx, ny, cx, cy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = None
    bestv = -10**18
    for dx, dy, nx, ny in valid:
        d_opp_now = king_dist(nx, ny, ox, oy)
        # Evasion or mild discouragement when opponent is near.
        if opp_close:
            base = 2.2 * d_opp_now
            # small center bias to avoid oscillation
            base -= 0.03 * king_dist(nx, ny, cx, cy)
        else:
            base = 0.6 * d_opp_now - 0.02 * king_dist(nx, ny, cx, cy)

        # Evaluate best resource we could capture next-ish from this move.
        best_res = -10**18
        for rx, ry in resources:
            d_me = king_dist(nx, ny, rx, ry)
            d_opp = king_dist(ox, oy, rx, ry)
            # Favor resources closer to us; punish those much closer to opponent.
            # Also encourage immediate proximity (lower d_me).
            v = 3.0 / (1 + d_me)
            v += 0.7 * (d_opp - d_me)  # positive if we are relatively closer
            v -= 0.05 * d_me
            # If this move lands on a resource cell, heavily prioritize.
            if nx == rx and ny == ry:
                v += 6.0
            if v > best_res:
                best_res = v

        # Strong penalty if this move allows opponent to be on top of us.
        # (We can't block directly, but we can avoid giving them immediate advantage.)
        v_total = base + best_res - (2.5 if d_opp_now <= 1 else (1.0 if d_opp_now == 2 else 0.0))
        if v_total > bestv:
            bestv = v_total
            best = (dx, dy)

    return [best[0], best[1]]