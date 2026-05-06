def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if len(moves) != 9:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_value(px, py):
        best = None
        for rx, ry in res:
            md = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer closer resources; strongly prefer those we can reach earlier than opponent.
            v = (od - md) * 3.0 - md * 0.6
            # Small bias toward center-ish to avoid dead-ends while racing.
            cx, cy = w // 2, h // 2
            v += -0.02 * (abs(rx - cx) + abs(ry - cy))
            if best is None or v > best[0]:
                best = (v, rx, ry)
        return best[0]

    best_move = (None, -10**9, sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = best_value(nx, ny)
        if v > best_move[1]:
            best_move = ((dx, dy), v, nx, ny)

    if best_move[0] is None:
        # Fallback: nearest resource direction among valid 4/diag
        tx, ty = min(res, key=lambda r: man(sx, sy, r[0], r[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if ok(sx + dx, sy + dy):
            return [dx, dy]
        if ok(sx + dx, sy):
            return [dx, 0]
        if ok(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    return [int(best_move[0][0]), int(best_move[0][1])]