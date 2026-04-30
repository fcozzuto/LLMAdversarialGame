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

    def sgn(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    # Primary goal: win races for resources (prefer targets where we are already closer than opponent).
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        race = do - ds  # positive means we are closer
        # Tie-break by resource position deterministically
        key = (-1 if race > 0 else 1, -race, ds, rx, ry)  # prefer race-positive, then larger race, then closer
        if best is None or key < best[0]:
            best = (key, rx, ry)

    if best is not None:
        _, tx, ty = best
    else:
        # If no resources visible, try to pressure opponent.
        tx, ty = ox, oy

    dx = sgn(tx - sx)
    dy = sgn(ty - sy)

    # If preferred step is illegal, pick legal step minimizing distance to target, with an opponent-block bias.
    pref_illegal = (sx + dx, sy + dy) in blocked or not (0 <= sx + dx < w and 0 <= sy + dy < h)
    if pref_illegal or (dx, dy) not in [(m[0], m[1]) for m in legal]:
        best_move = None
        for mdx, mdy in legal:
            nx, ny = sx + mdx, sy + mdy
            ds = cheb(nx, ny, tx, ty)
            # opponent race disruption: prefer moves that also increase our lead over opponent
            next_do = cheb(ox, oy, tx, ty)
            lead = ds - next_do  # smaller is better (more negative means we are closer)
            key = (lead, ds, (nx - sx) * (nx - sx) + (ny - sy) * (ny - sy), mdx, mdy)
            if best_move is None or key < best_move[0]:
                best_move = (key, mdx, mdy)
        return [int(best_move[1]), int(best_move[2])]

    return [int(dx), int(dy)]