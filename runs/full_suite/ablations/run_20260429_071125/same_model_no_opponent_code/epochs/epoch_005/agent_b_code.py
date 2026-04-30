def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            # Prefer moves that reduce distance to nearest resource,
            # and (secondarily) increase distance to opponent.
            d_to_res = min(cheb(nx, ny, r[0], r[1]) for r in resources)
            d_to_op = cheb(nx, ny, ox, oy)
            key = (-d_to_res, -d_to_op, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        if best is not None:
            return [int(best[0]), int(best[1])]

    tx, ty = w // 2, h // 2
    best = (0, 0)
    bd = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d = cheb(nx, ny, tx, ty)
        if d < bd:
            bd = d
            best = (dx, dy)
    return [int(best[0]), int(best[1])]