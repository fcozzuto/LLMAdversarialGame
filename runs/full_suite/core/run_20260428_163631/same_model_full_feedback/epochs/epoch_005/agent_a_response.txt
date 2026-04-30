def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort(key=lambda d: (d[0] == 0 and d[1] == 0, d[0] * d[0] + d[1] * d[1]))

    # Pick best resource by deterministic contest advantage (opponent closer is worse).
    best_target = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gap = od - sd  # higher means we are closer
        # Deterministic tie-breakers: maximize gap, then smaller self distance, then lexicographic position
        key = (-gap, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        # No resources: move toward opponent (or toward center if blocked).
        tx, ty = ox, oy
        if (tx, ty) == (sx, sy):
            tx, ty = (w // 2, h // 2)
    else:
        tx, ty = best_target

    # Choose safe move that greedily reduces distance to target; avoid increasing cheb too much.
    best_move = (0, 0)
    best_step_key = None
    curd = cheb(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer strictly improving; otherwise minimize nd; tie-break by move direction deterministically.
        improve = curd - nd
        step_key = (-improve, nd, dx, dy)
        if best_step_key is None or step_key < best_step_key:
            best_step_key = step_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]