def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestd = -10**9
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = -cheb(nx, ny, cx, cy)
            if d > bestd:
                bestd = d
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    # Choose resource by advantage: closer to self and farther from opponent.
    best_score = -10**18
    best_t = resources[0]
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Encourage taking contested resources only if we are meaningfully closer.
        score = (do - ds) * 2.0 - ds * 0.35
        if (rx, ry) == resources[0]:
            pass
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    rx, ry = best_t
    # Primary: move toward target.
    tx = 0 if rx == sx else (1 if rx > sx else -1)
    ty = 0 if ry == sy else (1 if ry > sy else -1)

    candidates = []
    primary = (tx, ty)
    # If primary blocked, we'll evaluate all moves.
    for dx, dy in moves:
        if not inb(sx + dx, sy + dy):
            continue
        nx, ny = sx + dx, sy + dy
        # Evaluate next step using same advantage heuristic for best resource.
        # Keep it cheap: only compare against current best target and nearest alternative.
        ds1 = cheb(nx, ny, rx, ry)
        do1 = cheb(ox, oy, rx, ry)
        base = (do1 - ds1) * 2.0 - ds1 * 0.35
        # Small preference for progressing toward target (lexicographic).
        prog = -cheb(nx, ny, rx, ry) - 0.1 * cheb(nx, ny, sx, sy)
        cand_score = base + prog
        if (dx, dy) == primary:
            cand_score += 0.25
        candidates.append((cand_score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]