def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_t = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in blocked:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; tie-break deterministically.
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        tx, ty = (w // 2, h // 2)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            d = cheb(nx, ny, tx, ty)
            key = (-d, nx, ny)  # minimize distance; deterministic tie-break
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        return best_move if best_key is not None else [0, 0]

    tx, ty = best_t
    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = cheb(nx, ny, tx, ty)
        # Primary: reduce our distance; Secondary: keep away from opponent if similar; Tertiary: determinism.
        opp_d = cheb(nx, ny, ox, oy)
        key = (-d, -opp_d, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]