def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If starting position is invalid, step to a nearby valid cell deterministically.
    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - b
        if dx < 0: dx = -dx
        dy = c - d
        if dy < 0: dy = -dy
        return dx + dy

    target = None
    if resources:
        best = None
        for x, y in resources:
            d = dist(x, sx, y, sy)
            if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
                best = (d, (x, y))
        target = best[1]
    else:
        target = (ox, oy)

    tx, ty = int(target[0]), int(target[1])

    best_move = (10**9, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist(nx, tx, ny, ty)
        # Prefer moving closer; tie-break by deterministic order via (nx, ny)
        if d < best_move[0] or (d == best_move[0] and (nx, ny) < best_move[1]):
            best_move = (d, (nx, ny))

    bx, by = best_move[1]
    return [bx - sx, by - sy]