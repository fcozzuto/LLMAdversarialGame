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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = r[0], r[1]
            if isinstance(tx, int) and isinstance(ty, int) and inb(tx, ty):
                rs.append((tx, ty))
    if not rs:
        return [0, 0]

    # Target selection: secure resources closer to us, but prefer where we're not clearly behind.
    # Key: minimize self_dist; then minimize (self_dist - opp_dist) => prefer opp_dist >= self_dist.
    best = None
    best_key = None
    for tx, ty in rs:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        key = (ds, ds - do, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    # Move selection: greedy step toward target among valid moves; deterministic tie-break.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_dist = cheb(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_dist or (d == best_dist and (dx, dy) < best_move):
            best_dist = d
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]