def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def resource_priority(rx, ry):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner (or deny), then by closeness to us.
        return (do - ds, -ds, -rx, -ry)

    if resources:
        best_res = None
        best_key = None
        for rx, ry in resources:
            k = resource_priority(rx, ry)
            if best_key is None or k > best_key:
                best_key = k
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        # No visible resources: move to center region deterministically.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            # Recompute competitiveness from this prospective position.
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            comp = do - ds  # higher means we stay ahead toward chosen resource
            # Also slightly discourage moving toward opponent generally.
            opp_d = cheb(nx, ny, ox, oy)
            val = (comp * 1000) - ds - (opp_d // 2)
        else:
            ds = cheb(nx, ny, tx, ty)
            opp_d = cheb(nx, ny, ox, oy)
            val = (-ds * 10) - (opp_d // 3)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying.
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]