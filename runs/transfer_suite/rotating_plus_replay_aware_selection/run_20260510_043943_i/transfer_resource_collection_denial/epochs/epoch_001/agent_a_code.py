def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    deltas.sort(key=lambda d: (abs(d[0]) + abs(d[1]), -abs(d[0]*d[1]), d[0], d[1]))

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return max(abs(ax - bx), abs(ay - by))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            key = (ds - 0.95 * do, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best if best is not None else ((w - 1) // 2, (h - 1) // 2)

    target = (tx, ty)
    curd = dist((sx, sy), target)
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), target)
        # Prefer moves that reduce distance; if tied, bias toward diagonal progress.
        key = (nd, abs(nx - target[0]) + abs(ny - target[1]),
               -(abs(dx) + abs(dy)), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    if best_move == (0, 0) and curd == 0 and resources:
        # Standing on a resource (or best-effort), keep still.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]