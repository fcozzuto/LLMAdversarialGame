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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
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

    # Strategic change: target resources using a stronger "win-first" bias against opponent proximity.
    # Choose target minimizing: 2*self_dist - opp_dist (prefer close to us and relatively far from opponent).
    best_t = None
    best_k = None
    for tx, ty in rs:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        k = (2 * ds - do, ds, tx, ty)
        if best_k is None or k < best_k:
            best_k = k
            best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_m = [0, 0]
    best_mv_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)

        # Also prefer staying on course toward the single best target, with minor obstacle-aware tie breaks.
        # Lexicographic: minimize myd, then minimize (myd - opd) => avoid being the slower claimant, then prefer diagonal alignment.
        align = 0 if dx == 0 or dy == 0 else 1
        k = (myd, myd - opd, -align, nx, ny)
        if best_mv_k is None or k < best_mv_k:
            best_mv_k = k
            best_m = [dx, dy]

    return best_m