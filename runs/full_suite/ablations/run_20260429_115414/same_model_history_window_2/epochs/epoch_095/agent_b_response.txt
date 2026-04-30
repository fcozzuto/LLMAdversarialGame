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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        ti = int(observation.get("turn_index") or 0)
        for dx, dy, nx, ny in legal:
            dres = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < dres:
                    dres = d
            dop = cheb(nx, ny, ox, oy)
            # Prefer decreasing distance to resources; keep some separation from opponent.
            # Deterministic tie-break: slight parity bias.
            cand = (-dres, dop, (dx + 1) + 3 * (dy + 1), (ti % 2) * (dx == 0))
            if best is None or cand > best[0]:
                best = (cand, [dx, dy])
        return best[1]
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            dcen = cheb(nx, ny, cx, cy)
            dop = cheb(nx, ny, ox, oy)
            cand = (-dcen, dop, (dx + 1) + 3 * (dy + 1))
            if best is None or cand > best[0]:
                best = (cand, [dx, dy])
        return best[1]