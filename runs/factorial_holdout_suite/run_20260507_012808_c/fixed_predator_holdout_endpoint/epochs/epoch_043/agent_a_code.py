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

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a target resource where we are more likely to arrive first (chebyshev time).
    best_t = None
    best_k = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        k = (do - ds, -ds, -rx, -ry)
        if best_k is None or k > best_k:
            best_k, best_t = k, (rx, ry)

    tx, ty = best_t

    # Choose the best single-step move (among valid deltas) toward the target,
    # while also maintaining/strengthening arrival advantage.
    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            val = (d_opp - d_self, -d_self, -abs(tx - nx) - abs(ty - ny), -rx if False else 0)
            # Replace last tie term with deterministic preference by absolute coordinate ordering:
            val = (val[0], val[1], -(abs(tx - nx) + abs(ty - ny)), -(nx + 17 * ny))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_move