def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obst = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obst)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            key = (od - myd, od, -myd, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_t = (rx, ry)
        if best_t is None:
            best_t = (0, 0)
    else:
        best_t = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = best_t
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        score = (-myd, od, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]