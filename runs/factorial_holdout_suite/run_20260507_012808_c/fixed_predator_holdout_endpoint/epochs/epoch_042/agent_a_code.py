def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_t = None
    best_k = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        k = (do - ds, -ds, -rx, -ry)
        if best_k is None or k > best_k:
            best_k, best_t = k, (rx, ry)
    tx, ty = best_t

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not move_ok(nx, ny):
                continue
            ns = cheb(nx, ny, tx, ty)
            no = cheb(ox, oy, tx, ty)
            self_adv = no - ns
            opp_space = cheb(nx, ny, ox, oy)
            # Prefer taking lead toward target, then getting closer, then avoiding being near opponent too soon.
            k = (self_adv, -ns, -opp_space, 0 if (dx == 0 and dy == 0) else 1, -dx, -dy)
            candidates.append((k, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]