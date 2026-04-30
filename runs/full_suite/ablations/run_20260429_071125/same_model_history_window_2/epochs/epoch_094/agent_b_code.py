def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_val = None
    target = None
    if resources:
        best_d = 10**9
        best_t = None
        for tx, ty in resources:
            d = cheb(sx, sy, tx, ty)
            if d < best_d or (d == best_d and (tx, ty) < best_t):
                best_d = d
                best_t = (tx, ty)
        target = best_t

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if target:
            # Prefer smallest distance to target; break ties by staying away from opponent.
            d_to_t = cheb(nx, ny, target[0], target[1])
            d_from_op = cheb(nx, ny, ox, oy)
            val = (d_to_t, -d_from_op, dx, dy)
        else:
            # No resources: keep distance from opponent, deterministic by direction order.
            d_from_op = cheb(nx, ny, ox, oy)
            val = (-d_from_op, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is not None:
        return [int(best[0]), int(best[1])]

    # Fallback (should rarely happen): wait if legal else first legal move deterministically.
    if valid(sx, sy):
        return [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]