def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # Precompute resource priorities from our current position
    # Key: maximize lead, then minimize our distance, then closer to center to reduce stalling
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_targets = []
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = opd - myd
        myd2 = myd + 0.001 * (cheb(rx, ry, sx, sy))
        center = abs(rx - cx) + abs(ry - cy)
        best_targets.append((lead, -myd2, -center, rx, ry))
    best_targets.sort(reverse=True)
    # limit to a few for speed/determinism
    best_targets = best_targets[:5]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # evaluate using top target candidates only
        val = None
        for lead, neg_myd, neg_center, rx, ry in best_targets:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            new_lead = opd - myd
            # lexicographic maximization: higher lead, then smaller myd, then preference for same top target order
            score = (new_lead, -myd, neg_center)
            if val is None or score > val:
                val = score
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]