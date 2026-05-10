def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate this move by the best resource we could plausibly secure next.
        move_best = None
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            reach_flag = 1 if myd <= opd else 0
            adv = opd - myd
            # Prefer moving that actually shortens my distance to that resource.
            curd = man(sx, sy, rx, ry)
            progress = curd - myd
            key = (reach_flag, adv, progress, -myd, -opd, -(rx + ry))
            if move_best is None or key > move_best:
                move_best = key
        if move_best is None:
            continue
        if best_key is None or move_best > best_key:
            best_key = move_best
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]