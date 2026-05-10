def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cells = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                cells.append((nx, ny, dx, dy))
    if not cells:
        return [0, 0]

    valid = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obs:
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    valid.sort()  # deterministic tie-break

    # One-step lookahead: pick move that maximizes eventual advantage vs opponent for nearest winnable resource.
    best = None
    for nx, ny, mdx, mdy in cells:
        best_for_move = None
        for rx, ry in valid:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer
            # prefer: higher lead, then closer to secure (smaller ds), then prioritize earlier in sorted order
            tup = (lead, -ds, -abs(ry - (h - 1) / 2.0))
            if best_for_move is None or tup > best_for_move[0]:
                best_for_move = (tup, rx, ry)
        # discourage moves that don't improve our distance to the best candidate resource
        # (simple: compare to current best distance)
        if best_for_move is None:
            move_score = (-10**9, 0, 0)
        else:
            _, rx, ry = best_for_move
            cur_ds = cheb(sx, sy, rx, ry)
            nxt_ds = cheb(nx, ny, rx, ry)
            move_score = (best_for_move[0], -(nxt_ds), (cur_ds - nxt_ds))
        if best is None or move_score > best[0]:
            best = (move_score, mdx, mdy)

    return [int(best[1]), int(best[2])]