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

    def pick_target():
        if not resources:
            return None
        best = None
        best_key = None
        for cx, cy in resources:
            self_d = cheb(sx, sy, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            key = (opp_d - self_d, -self_d, cx, cy)  # prioritize advantage, then nearer, deterministic tie-break
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    target = pick_target()
    if target is None:
        best_move = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best_move = [dx, dy]
        return best_move

    tx, ty = target
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_to_target = cheb(nx, ny, tx, ty)
        opp_dist = cheb(nx, ny, ox, oy)
        key = (-dist_to_target, opp_dist, dx, dy)  # closest to target; then away from opponent; deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best