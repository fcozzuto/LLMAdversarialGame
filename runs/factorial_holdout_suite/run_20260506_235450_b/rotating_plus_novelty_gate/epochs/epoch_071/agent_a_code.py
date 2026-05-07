def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_u = -10**18
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if blocked(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds == 0:
            u = 10**12
        else:
            u = (do - ds) * 50 - ds
            if do < ds:
                u -= 25  # avoid resources opponent is nearer to
        if u > best_u:
            best_u = u
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_d = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_d:
            best_d = d
            best_move = (dx, dy)
        elif d == best_d:
            # break ties by preferring moves that improve self advantage over opponent for current target
            if (cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)) < (cheb(sx, sy, tx, ty) - cheb(ox, oy, tx, ty)):
                best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]