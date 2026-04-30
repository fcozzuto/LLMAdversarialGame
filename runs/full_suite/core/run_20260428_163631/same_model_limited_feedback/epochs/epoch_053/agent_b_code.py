def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

    target = None
    best = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        cand = (do - ds, -ds, -abs(rx - sx) - abs(ry - sy))
        if best is None or cand > best:
            best = cand
            target = (rx, ry)

    if target is None:
        return [0, 0]

    tx, ty = target
    best_step = None
    best_step_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        oppd = dist((ox, oy), (tx, ty))
        val = (-(nd), (oppd - nd), -abs(tx - nx) - abs(ty - ny))
        if best_step is None or val > best_step_val:
            best_step_val = val
            best_step = [dx, dy]

    if best_step is None:
        return [0, 0]
    return best_step