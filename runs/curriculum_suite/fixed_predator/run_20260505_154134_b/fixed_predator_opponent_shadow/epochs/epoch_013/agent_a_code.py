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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_cell = None
    best_key = (-10**18, -10**18)
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        # Prefer resources where we have an advantage; otherwise prefer being closer.
        key = (opp_d - self_d, -self_d)
        if key > best_key:
            best_key = key
            best_cell = (cx, cy)

    tx, ty = best_cell
    curd = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_mkey = (-10**18, 10**18, 10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        opp_nd = cheb(ox, oy, tx, ty)  # unchanged this turn; keep tie-break consistent
        # Primary: reduce distance to chosen target; secondary: maximize advantage on that target; then proximity.
        mkey = (-(nd - curd), (opp_nd - nd), -nd)
        # Encode to fixed tuple ordering: (reduce, advantage, closer)
        if mkey > (best_mkey[0], best_mkey[1], best_mkey[2]):
            best_mkey = (mkey[0], mkey[1], mkey[2])
            best_move = [dx, dy]

    # Safety fallback if all moves invalid (shouldn't happen): stay.
    if not valid(sx, sy):
        return [0, 0]
    if best_move == [0, 0]:
        # Try any valid move that increases distance from opponent slightly (avoid being trapped).
        fallback = [0, 0]
        fbv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > fbv:
                fbv = v
                fallback = [dx, dy]
        return fallback
    return best_move