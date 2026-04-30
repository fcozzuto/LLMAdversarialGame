def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # No resources visible: move to reduce opponent distance to disrupt timing
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18
    best_ds = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_val = -cheb(nx, ny, ox, oy) * 0.2  # slight anti-kiting
        move_ds_best = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            contest = do - ds  # positive means we are closer or equal
            on_r = 1 if (nx == rx and ny == ry) else 0
            # Prefer taking/contesting resources; strongly reward immediate pickup.
            v = contest * 12 - ds * 2 + on_r * 60
            if ds < move_ds_best:
                move_ds_best = ds
            if v > move_val:
                move_val = v
        # Tie-break: closer to the best evaluated resource next.
        if move_val > best_val or (move_val == best_val and move_ds_best < best_ds):
            best_val, best_ds, best_move = move_val, move_ds_best, [dx, dy]

    return [int(best_move[0]), int(best_move[1])]