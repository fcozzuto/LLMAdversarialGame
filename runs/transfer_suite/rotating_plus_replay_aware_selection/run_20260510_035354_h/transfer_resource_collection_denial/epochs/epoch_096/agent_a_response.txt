def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a resource we can secure earlier than the opponent; if tied, prefer closer one.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # resource_denier: if opponent is close, we bias more toward items where we are ahead
        key = (ds - 1.35 * do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Evaluate each possible move deterministically by resulting position (assume invalid stays put).
    best_m = [0, 0]
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        ns = md(nx, ny, tx, ty)
        # discourage stepping away from a likely contested target
        cont = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            ds2 = md(nx, ny, rx, ry)
            do2 = md(ox, oy, rx, ry)
            if do2 <= ds2:  # opponent can reach no later
                cont += 1
        opp_future = md(ox, oy, tx, ty)
        # Lower is better
        sc = (ns - 1.1 * opp_future, ns, cont, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_s is None or sc < best_s:
            best_s = sc
            best_m = [dx, dy]
    return [int(best_m[0]), int(best_m[1])]