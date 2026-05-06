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

    def target_pick():
        if not resources:
            return (sx, sy)
        best = None
        best_key = None
        any_ahead = False
        for cx, cy in resources:
            sd = cheb(sx, sy, cx, cy)
            od = cheb(ox, oy, cx, cy)
            if sd < od:
                any_ahead = True
                key = (1, od - sd, -sd, -cx, -cy)
            else:
                key = (0, -sd, -cx, -cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        # Prefer "we can beat opponent" if exists
        if any_ahead:
            # re-evaluate strictly for sd < od
            for cx, cy in resources:
                sd = cheb(sx, sy, cx, cy)
                od = cheb(ox, oy, cx, cy)
                if sd < od:
                    key = (1, od - sd, -sd, -cx, -cy)
                    if key == best_key:
                        best = (cx, cy)
                        break
        return best

    tx, ty = target_pick()

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_mv = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # primary: maximize relative advantage; secondary: minimize our distance
        key = (od - sd, -sd, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]]