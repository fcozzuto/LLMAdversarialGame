def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs if p is not None and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target = None
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = cheb(sx, sy, rx, ry)
        if best is None or d < best:
            best = d
            target = (rx, ry)

    if target is None:
        tx, ty = ox, oy
    else:
        tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Prefer reducing distance to target; break ties by staying safer around obstacles.
        penalty = 0
        for ax, ay in obstacles:
            mx = nx - ax
            if mx < 0:
                mx = -mx
            my = ny - ay
            if my < 0:
                my = -my
            m = mx if mx > my else my
            if m == 1:
                penalty += 3
        val = (d_me - (d_op // 10), d_me, penalty, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]