def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        bestk = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach first, then closer, then higher opponent distance.
            k = (0 if ds <= do else 1, ds, -do, rx, ry)
            if bestk is None or k < bestk:
                bestk = k
                best = (rx, ry)
        tx, ty = best if best is not None else (w // 2, h // 2)

    do_target = cheb(ox, oy, tx, ty)
    bestm = (0, 0)
    bestkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds_next = cheb(nx, ny, tx, ty)
        key = (0 if ds_next <= do_target else 1, ds_next, dx * dx + dy * dy, nx, ny)
        if bestkey is None or key < bestkey:
            bestkey = key
            bestm = (dx, dy)
    return [bestm[0], bestm[1]]