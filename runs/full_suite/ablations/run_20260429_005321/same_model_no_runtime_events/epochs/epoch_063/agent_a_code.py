def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    best_target = None
    best_metric = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds <= do:
            # Prefer resources where we are at least as close; then minimize our distance.
            metric = (0, ds, -do, rx, ry)
        else:
            # If none, we'll consider these later.
            metric = (1, do - ds, ds, rx, ry)
        if best_metric is None or metric < best_metric:
            best_metric = metric
            best_target = (rx, ry)

    # If closest resource is actually strongly worse, still choose step that maximizes advantage.
    def score_cell(x, y, tx, ty):
        ds = cheb(x, y, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds  # bigger is better
        opp_close = cheb(x, y, ox, oy)
        return (adv, -ds, opp_close)

    tx, ty = best_target if best_target is not None else (sx, sy)
    best_move = [0, 0]
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score_cell(nx, ny, tx, ty)
        # Tie-break deterministically by preferring moves that reduce distance to our target, then avoid opponent.
        if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < tuple(best_move)):
            best_sc = sc
            best_move = [int(dx), int(dy)]
    return [int(best_move[0]), int(best_move[1])]