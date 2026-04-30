def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
    if not resources:
        # deterministic: move toward center while avoiding blocked
        cx, cy = (w - 1) // 2, (h - 1) // 2
        moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        best = (10**9, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                continue
            d = max(abs(nx - cx), abs(ny - cy))
            if d < best[0]:
                best = (d, (dx, dy))
        return best[1] if best[1] is not None else [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # pick target resource: prefer ones we can reach sooner than opponent, tie-break by centrality
    midx, midy = (w - 1) // 2, (h - 1) // 2
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # maximize: opponent slower + our sooner; then prefer being close to center for stability
        key = (do - ds, -ds, -(abs(rx - midx) + abs(ry - midy)))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    best_mv = (0, 0)
    best_score = None
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # primary: reduce our distance; secondary: increase separation vs opponent time advantage
        score = (no - ns, -ns, -cheb(nx, ny, midx, midy))
        if best_score is None or score > best_score:
            best_score = score
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]