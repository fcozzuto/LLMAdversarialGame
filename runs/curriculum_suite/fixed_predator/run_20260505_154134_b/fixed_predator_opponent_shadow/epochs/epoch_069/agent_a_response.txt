def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]
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

    def pick_target():
        best = resources[0]
        best_key = None
        for cx, cy in resources:
            self_d = cheb(sx, sy, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            key = (opp_d - self_d, -self_d, -(cx + 31 * cy))
            if best_key is None or key > best_key:
                best_key = key
                best = (int(cx), int(cy))
        return best

    tx, ty = pick_target()

    best_move = (0, 0)
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            self_dn = cheb(nx, ny, tx, ty)
            opp_dn = cheb(ox, oy, tx, ty)
            gain = opp_dn - self_dn
            block = - (1 if (nx, ny) in obs else 0)
            pref = -(abs(nx - tx) + abs(ny - ty))
            key = (gain, -self_dn, -max(abs(nx - ox), abs(ny - oy)), pref + block)
            if best_score is None or key > best_score:
                best_score = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]