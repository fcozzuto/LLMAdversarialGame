def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, ox, oy)
            key = (0, d, -(nx + ny))
            if best_key is None or key > best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    # Target resources that we can reach significantly sooner than the opponent.
    best = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_adv = None
        best_res = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer than opponent
            # small tiebreak to prefer earlier progress toward nearer resources overall
            key2 = (adv, -(ds + do), -(rx + ry))
            if best_adv is None or key2 > best_adv:
                best_adv, best_res = key2, (rx, ry)
        # Prefer moves that maximize our advantage; if tied, advance directly toward that best resource.
        rx, ry = best_res
        ds_now = cheb(nx, ny, rx, ry)
        do_now = cheb(ox, oy, rx, ry)
        # Also add mild opponent-distance term to avoid giving them easy alternative captures.
        key = (best_adv[0], -ds_now, -(do_now), (nx + ny))
        if best_key is None or key > best_key:
            best_key, best = key, (dx, dy)

    return [best[0], best[1]]