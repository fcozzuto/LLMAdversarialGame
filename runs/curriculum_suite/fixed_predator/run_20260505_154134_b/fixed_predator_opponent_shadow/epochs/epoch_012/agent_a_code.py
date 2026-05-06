def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def norm_score(tx, ty):
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        return (od - sd, -(sd))

    if not resources:
        best = (-(10**9), (0, 0))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            cand = (v, (dx, dy))
            if cand > best:
                best = cand
        return [best[1][0], best[1][1]]

    # Pick resource where we have the best distance advantage; deterministic tie-break by position.
    best_t = None
    best_k = None
    for cx, cy in resources:
        k = norm_score(cx, cy)
        if best_t is None or k > best_k or (k == best_k and (cx, cy) < best_t):
            best_t, best_k = (cx, cy), k

    tx, ty = best_t

    # Move one step toward target, but avoid positions where opponent is much closer.
    best_move = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        margin_after = (opp_d - self_d)
        # Tie-break: prefer smaller self_d then lexicographically smaller move.
        key = (margin_after, -(self_d), -dx, -dy)
        if key > best_move:
            best_move = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]