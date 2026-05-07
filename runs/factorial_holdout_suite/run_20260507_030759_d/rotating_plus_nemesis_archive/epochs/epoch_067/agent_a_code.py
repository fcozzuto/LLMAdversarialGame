def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    if resources:
        best = None
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
                best = (d, (x, y))
        target = best[1]
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for x, y in corners:
            d = cheb(ox, oy, x, y)
            if best is None or d > best[0] or (d == best[0] and (x, y) < best[1]):
                best = (d, (x, y))
        target = best[1]

    tx, ty = target
    best_val = None
    best_move = (0, 0)
    # Prefer closer to target, and if tie prefer farther from opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        v1 = cheb(nx, ny, tx, ty)
        v2 = cheb(nx, ny, ox, oy)
        val = (v1, -v2)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]