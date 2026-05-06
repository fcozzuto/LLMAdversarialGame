def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set(tuple(p) for p in obstacles)
    resources = observation.get("resources") or []
    if resources is None:
        resources = []

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_move = [0, 0]

    targets = resources if resources else [(cx, cy)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        rdist = min(man(nx, ny, rx, ry) for rx, ry in targets)
        odist = man(nx, ny, ox, oy)
        key = (rdist, -odist, nx, ny, dx, dy)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return best_move