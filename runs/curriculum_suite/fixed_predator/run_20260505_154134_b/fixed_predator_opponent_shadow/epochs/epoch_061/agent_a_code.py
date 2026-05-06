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

    if not resources:
        return [0, 0]

    dirs = (-1, 0, 1)
    best = None
    best_key = None
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            # evaluate by best resource for this prospective cell
            best_val = None
            for cx, cy in resources:
                self_d = cheb(nx, ny, cx, cy)
                opp_d = cheb(ox, oy, cx, cy)
                # prefer resources we can reach earlier; otherwise still prefer denying by opp advantage
                val = (opp_d - self_d, -self_d, -abs(nx - sx) - abs(ny - sy), -cx, -cy)
                if best_val is None or val > best_val:
                    best_val = val
            key = best_val
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]