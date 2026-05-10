def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_score(nx, ny, target):
        tx, ty = target
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        return (od - sd, -sd, -tx, -ty)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                k = ( -cheb(nx, ny, tx, ty), -cheb(ox, oy, tx, ty), -dx, -dy)
                if best is None or k > best[0]:
                    best = (k, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_target = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        k = (od - sd, -sd, -rx, -ry)
        if best_key is None or k > best_key:
            best_key = k
            best_target = (rx, ry)

    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        k = move_score(nx, ny, best_target)
        if best_move is None or k > best_move[0]:
            best_move = (k, dx, dy)

    if best_move is not None:
        return [best_move[1], best_move[2]]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]