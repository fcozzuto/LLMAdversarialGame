def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    valid = [(dx, dy, sx + dx, sy + dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # If no visible resources, drift toward center to keep options.
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            d = dist(nx, ny, tx, ty)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    best_move = None
    for dx, dy, nx, ny in valid:
        # Evaluate this move by the best "resource we can claim earlier than opponent"
        # then breaking ties by global advantage.
        best_claim_score = None
        best_secondary = None
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Claim if we can arrive not later than opponent
            claim = (myd <= opd)
            # Deterministic scoring: prioritize immediate claims, then nearer overall.
            claim_score = (1 if claim else 0, -myd, -(opd - myd) if claim else -(opd), -rx, -ry)
            secondary = (myd - opd, myd, opd, rx, ry)
            if best_claim_score is None or claim_score > best_claim_score or (claim_score == best_claim_score and secondary < best_secondary):
                best_claim_score = claim_score
                best_secondary = secondary

        # Also encourage moves that reduce distance to the closest resource overall.
        mind_all = None
        for rx, ry in resources:
            d = dist(nx, ny, rx, ry)
            if mind_all is None or d < mind_all:
                mind_all = d

        # Prefer claim-capable moves; then smaller mind_all.
        key = (best_claim_score[0] if best_claim_score is not None else 0, mind_all, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [best_move[1], best_move[2]]