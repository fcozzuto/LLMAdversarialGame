def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick target where we have the biggest estimated advantage (considering obstacles only as impassable cells)
    best_target = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer large advantage (opponent farther than us). If tie, prefer closer.
        key = (-(d_op - d_me), d_me, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Evaluate our next move assuming opponent will also greedily minimize their distance to the same target next turn.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; emulate deterministically

        our_d_next = cheb(nx, ny, tx, ty)

        # Opponent greedy next distance to target
        opp_best = None
        for odx, ody in moves:
            px, py = ox + odx, oy + ody
            if not inb(px, py):
                px, py = ox, oy
            d = cheb(px, py, tx, ty)
            if opp_best is None or d < opp_best:
                opp_best = d

        # We want to maximize (opp_next - our_next). Tie-break: minimize our_next, then stable coords.
        advantage_next = (opp_best - our_d_next)
        mkey = (-advantage_next, our_d_next, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]