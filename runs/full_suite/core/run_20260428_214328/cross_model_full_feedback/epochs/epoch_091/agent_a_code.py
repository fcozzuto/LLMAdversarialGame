def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def d(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target = None
    if resources:
        best = None
        for x, y in resources:
            ds = d((sx, sy), (x, y))
            do = d((ox, oy), (x, y))
            # Prefer resources where we arrive earlier; then closest; then deterministic.
            cand = (ds - do, ds, x, y)
            if best is None or cand < best:
                best = cand
                target = (x, y)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if target is None:
        # Deterministic fallback: stay if possible, else first valid move in order.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    tx, ty = target
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_to_target = d((nx, ny), (tx, ty))
        cand = (dist_to_target, abs(dx), abs(dy), dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand
            best_dxdy = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_dxdy[0], best_dxdy[1]]