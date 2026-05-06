def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    if not resources:
        return [0, 0]

    def pick_target():
        best = None
        best_key = None
        for cx, cy in resources:
            self_d = cheb(sx, sy, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # prefer resources where opponent is closer than us, then where we are closer
            key = (opp_d - self_d, -self_d, -cx, -cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    tx, ty = pick_target()

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            # minimize self distance to chosen target; maximize opponent distance (i.e., delay steal)
            key = (-self_d, opp_d, -abs(nx - tx), -abs(ny - ty), dx, dy)
            cand.append((key, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]