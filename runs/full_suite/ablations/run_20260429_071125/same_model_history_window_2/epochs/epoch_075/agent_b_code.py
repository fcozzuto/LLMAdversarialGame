def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if any(x == sx and y == sy for x, y in resources):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        # target where we are relatively closer than opponent; tie-break deterministically by (x,y)
        best = None
        best_val = -10**9
        for (x, y) in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            val = (do - ds) * 1000 - ds  # prefer stealing; then closer
            if val > best_val or (val == best_val and ((x, y) < best)):
                best_val = val
                best = (x, y)
        tx, ty = best
    else:
        # no resources visible: drift toward center while staying valid
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_d = 10**9
    best_t = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # secondary: keep away from opponent slightly to reduce contest risk
        td = cheb(nx, ny, ox, oy)
        if d < best_d or (d == best_d and (td > best_t or (td == best_t and (dx, dy) < tuple(best_move)))):
            best_d = d
            best_t = td
            best_move = [dx, dy]

    return best_move