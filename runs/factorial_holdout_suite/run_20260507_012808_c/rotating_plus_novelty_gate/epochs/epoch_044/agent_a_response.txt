def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else int(sx))
    sy = 0 if sy < 0 else (h - 1 if sy >= h else int(sy))
    ox = 0 if ox < 0 else (w - 1 if ox >= w else int(ox))
    oy = 0 if oy < 0 else (h - 1 if oy >= h else int(oy))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    if not resources:
        tx, ty = (w - 1 - sx, h - 1 - sy)
    else:
        best = None
        # resource denier: prefer resources where we are closer than opponent
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            ahead = od - myd
            # key: maximize ahead, then prefer smaller my distance, then deterministic position
            key = (-ahead, myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # choose move that maximizes our advantage at next step toward target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = clamp(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                nx, ny = sx, sy
                dx, dy = 0, 0
            moves.append((dx, dy, nx, ny))
    # opponent doesn't move; evaluate based on distance difference at next state
    best_mv = None
    best_key = None
    for dx, dy, nx, ny in moves:
        my_next = cheb(nx, ny, tx, ty)
        op_next = cheb(ox, oy, tx, ty)
        # primary: minimize (my_next - op_next) (more negative is better)
        key = (my_next - op_next, my_next, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]