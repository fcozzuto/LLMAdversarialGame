def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target where we have a favorable distance gap.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        key = (opd - myd, -myd)  # maximize (opd - myd), then minimize myd
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = (ox, oy) if best_t is None else best_t

    best_score = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Encourage closing to target, but only if we don't give up too much to opponent.
        score = (opd - myd) * 10 - myd - (1 if (dx == 0 and dy == 0) else 0)

        # Extra tie-break: prefer moves that keep us closest among nearby targets.
        if resources:
            # compute a tiny "threat" only for the nearest resource(s) by Manhattan
            near = None
            near_d = None
            for rx, ry in resources:
                if not inb(rx, ry) or (rx, ry) in obstacles:
                    continue
                d = man(nx, ny, rx, ry)
                if near_d is None or d < near_d:
                    near_d = d
                    near = (rx, ry)
            if near is not None:
                score += (man(ox, oy, near[0], near[1]) - near_d)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]