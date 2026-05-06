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
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target():
        best = None
        best_key = None
        for cx, cy in resources:
            self_d = cheb(sx, sy, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            key = (opp_d - self_d, -self_d, cx, cy)  # prefer places we can reach at least as fast
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    target = best_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)  # proxy: keep away from opponent while approaching target
        step_adv = (cheb(ox, oy, tx, ty) - d_to_t)  # positive means we are closer than opponent would be (heuristic)
        val = (step_adv, -d_to_t, d_opp, dx, dy)  # deterministic tie-break
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]