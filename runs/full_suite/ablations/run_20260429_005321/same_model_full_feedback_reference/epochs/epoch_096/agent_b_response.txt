def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_t = resources[0]
        best_val = -10**18
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            v = (do - ds) * 1000 - (tx + ty) * 0.0001 - ds * 0.01
            if v > best_val:
                best_val = v
                best_t = (tx, ty)

        tx, ty = best_t
        best_move = (0, 0)
        best_mval = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            ds2 = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # prefer reducing our distance while not giving opponent an advantage
            mval = (do - ds2) * 1000 - ds2 * 0.01
            # slight preference to approach target along both axes when possible
            mval -= (0.001 * (abs((tx - nx)) + abs((ty - ny))))
            if mval > best_mval:
                best_mval = mval
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move to deny space / approach opponent-middle by deterministic rule
    cx, cy = (w - 1) // 2, (h - 1) // 2
    tx, ty = cx, cy
    best_move = (0, 0)
    best_mval = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # prefer moves that reduce our distance to center while increasing distance from opponent
        mval = -cheb(nx, ny, tx, ty) * 10 + cheb(nx, ny, ox, oy) * 0.01
        if mval > best_mval:
            best_mval = mval
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]