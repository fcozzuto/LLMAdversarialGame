def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Deterministic neighbor ordering (including stay)
    neigh = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def pick_target():
        if resources:
            best = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = cheb(sx, sy, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Bias: prioritize reachability for self; punish resources opponent can contest sooner.
                # Deterministic tie-break by coordinates.
                key = (ds - 2 * do, ds, -do, rx, ry)
                if best is None or key < best[0]:
                    best = (key, (rx, ry))
            if best is not None:
                return best[1]
        # No visible resources: move to the quadrant that is farther from opponent and nearer to center.
        cx, cy = w // 2, h // 2
        candidates = []
        for tx, ty in [(0, cy), (w-1, cy), (cx, 0), (cx, h-1), (cx, cy)]:
            if legal(tx, ty) or (tx, ty) == (sx, sy):
                candidates.append((tx, ty))
        if not candidates:
            candidates = [(sx, sy)]
        best = None
        for tx, ty in candidates:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            key = (-do, ds, tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        return best[1]

    tx, ty = pick_target()
    best_move = (0, 0)
    best_key = None

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Move that decreases self distance to target; also slightly increases opponent distance.
        dself = cheb(nx, ny, tx, ty)
        dopp = cheb(nx, ny, ox, oy)
        # Tie-break deterministically: prefer moves with lower dself, higher dopp, then dx,dy.
        key = (dself, -dopp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]