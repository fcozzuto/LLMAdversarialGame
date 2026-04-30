def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Target: resource we reach earlier than opponent; break ties deterministically
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, -rx, -ry)  # maximize advantage, then closer, then deterministic
        if best is None or key > best_key:
            best = (int(rx), int(ry))
            best_key = key

    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    # Choose next step minimizing our distance to target while avoiding obstacles
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            ns = cheb(nx, ny, tx, ty)
            no = cheb(ox, oy, tx, ty)
            candidates.append((ns, -no, -dx, -dy, nx, ny))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=False)
    ns, _, _, _, nx, ny = candidates[0]
    return [nx - sx, ny - sy]