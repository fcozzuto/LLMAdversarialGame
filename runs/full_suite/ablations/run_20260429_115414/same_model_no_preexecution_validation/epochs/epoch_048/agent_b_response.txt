def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_key = None

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            best_adv = -10**9
            best_dme = 10**9
            for tx, ty in resources:
                dme = cheb(nx, ny, tx, ty)
                dop = cheb(ox, oy, tx, ty)
                adv = dop - dme
                if adv > best_adv or (adv == best_adv and dme < best_dme):
                    best_adv = adv
                    best_dme = dme
            # Prefer moves that give the best advantage; then reduce our distance to that target; then anti-collision bias
            key = (best_adv, -best_dme, -(nx + ny))
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            # Go toward center while keeping away from opponent
            dcent = cheb(nx, ny, int(cx), int(cy))
            dout = cheb(nx, ny, ox, oy)
            key = (-dcent, -dout, -(nx + ny))
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]