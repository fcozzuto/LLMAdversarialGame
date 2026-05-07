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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs or not inside(x, y)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds_resource(r):
        return isinstance(r, (list, tuple)) and len(r) >= 2 and isinstance(r[0], int) and isinstance(r[1], int) and 0 <= r[0] < w and 0 <= r[1] < h and (r[0], r[1]) not in obs

    candidates = [r for r in resources if in_bounds_resource(r)]
    if not candidates:
        return [0, 0]

    # Pick a target that we can reach sooner, while also preferring row-races against a sweep-row opponent:
    # assume opponent tends to move through rows, so bias towards resources whose row is "near" our current row advantage.
    best_r = None
    best_score = -10**18
    for r in candidates:
        rx, ry = r[0], r[1]
        du = cheb(sx, sy, rx, ry)
        dov = cheb(ox, oy, rx, ry)
        # relative advantage; small tie-break on how aligned the opponent row sweep is.
        rel = dov - du
        row_bias = -abs(ry - oy) * 0.05  # prefer rows closer to where opponent is right now
        score = rel * 100 - du + row_bias
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    tx, ty = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        du2 = cheb(nx, ny, tx, ty)
        dov2 = cheb(ox, oy, tx, ty)
        rel2 = dov2 - du2
        # small preference to reduce distance to target and keep relative advantage high
        val = rel2 * 100 - du2
        # deterministic tie-break: prefer larger x then larger y then staying last
        if val > best_val or (val == best_val and (nx, ny) > (sx + best_m[0], sy + best_m[1])):
            best_val = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]