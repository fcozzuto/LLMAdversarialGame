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
        u = (do - ds) * 30 - ds  # strong preference for resources we can take first/earlier
        if u > best_u:
            best_u = u
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cur_d = cheb(sx, sy, tx, ty)
    best_step = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer steps that reduce our distance; slight bias to keep ahead of opponent.
        step_score = (cur_d - nd) * 100 - nd
        step_score += (cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)) * 0  # deterministic no-op bias slot
        if step_score > best_score:
            best_score = step_score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]