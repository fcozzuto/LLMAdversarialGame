def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose target: maximize opponent lead being negative (i.e., make (od-sd) large), then closest ours.
    best = None
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer larger (od - sd); then smaller sd; then larger od; then coords.
        key = (-(od - sd), sd, -od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    if best is None:
        return [0, 0]

    tx, ty = best[1]
    if (sx, sy) == (tx, ty):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Primary: reduce our distance; Secondary: prefer moves that do not let opponent get closer (use no - ns proxy).
        # Tertiary: prefer staying less (deterministic).
        key = (ns, -(no - ns), abs(dx) + abs(dy), dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    if best_move is None:
        return [0, 0]
    return best_move[1]