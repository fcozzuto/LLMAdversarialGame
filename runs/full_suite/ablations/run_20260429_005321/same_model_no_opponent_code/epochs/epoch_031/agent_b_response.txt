def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def best_resource():
        if not resources:
            return None
        best_r = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier (smaller advantage gap).
            key = (ds - do, ds, -((rx + ry) & 1), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        return best_r

    target = best_resource()

    if target is None:
        # No resources visible: drift toward center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            key = (cheb(nx, ny, cx, cy), abs((nx + ny) - (x + y)))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [int(best[1]), int(best[2])]

    tx, ty = target
    best_move = None
    for dx, dy, nx, ny in legal:
        ds_new = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Primary: reach target sooner; Secondary: secure turn advantage; Tertiary: minimize distance.
        key = (ds_new - do, ds_new, cheb(nx, ny, tx, ty), -((nx + ny) & 1), nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [int(best_move[1]), int(best_move[2])]