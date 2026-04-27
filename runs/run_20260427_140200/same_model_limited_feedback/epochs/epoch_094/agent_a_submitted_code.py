def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource_dist(x, y):
        if not resources:
            return None
        best_ds = None
        best_do = None
        for r in resources:
            try:
                rx, ry = int(r[0]), int(r[1])
            except:
                continue
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prefer resources where we are closer than opponent, but still consider nearest
            adv = do - ds
            if best_ds is None or adv > best_do:
                best_ds, best_do = ds, adv
        return best_ds

    if resources:
        best_score = None
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            # score: maximum advantage against opponent for the best target
            score = 0
            for r in resources:
                try:
                    rx, ry = int(r[0]), int(r[1])
                except:
                    continue
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                adv = do - ds
                if adv > score:
                    score = adv
            # tie-break: prefer closer to some resource
            ds_min = best_resource_dist(nx, ny)
            key = (score, -ds_min if ds_min is not None else 0)
            if best_score is None or key > best_score:
                best_score = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: go toward center while avoiding obstacles
    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        distc = cheb(nx, ny, int(round(cx)), int(round(cy)))
        # prefer smaller center distance; deterministic tie-break via dx,dy ordering
        key = (-distc, -abs(dx), -abs(dy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]