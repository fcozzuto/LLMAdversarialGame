def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by): return max(abs(ax - bx), abs(ay - by))
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    target = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer being closer; if tie, prefer farthest from opponent and then closer to me.
        key = (-(do - dm), dm, do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    # If no resources, move to reduce distance to opponent
    if target is None:
        target = (ox, oy)

    tx, ty = target
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        # Also discourage stepping into squares that are closer for the opponent.
        opp_closeness = cheb(ox, oy, nx, ny)  # higher means more opposition reachability
        # Prefer smaller d_to_target; then prefer keeping opponent far from target-equilibrium.
        score = (d_to_target, opp_closeness)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]