def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [w - 1, h - 1]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best_move = (0, 0)
        best_key = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            k = (-cheb(nx, ny, ox, oy), nx, ny)
            if k < best_key:
                best_key = k
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best_res = None
    best_key = (10**9, 10**9, 10**9)
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer closer to us; strongly prefer if we're not behind opponent.
        behind = 0 if du <= do else 2
        k = (du + behind, do, rx + 100 * ry)
        if k < best_key:
            best_key = k
            best_res = (rx, ry)

    tx, ty = best_res
    best_move = (0, 0)
    best_key = (10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        # Mild obstacle/centering bias by preferring moves that keep us away from opponent.
        oppd = cheb(nx, ny, ox, oy)
        k = (dist, -oppd, nx + 100 * ny)
        if k < best_key:
            best_key = k
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]