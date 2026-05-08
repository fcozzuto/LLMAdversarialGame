def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(tuple(o) for o in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if resources:
        ds_best = None
        target = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            if ds_best is None or ds < ds_best:
                ds_best = ds
                target = (rx, ry)
        tx, ty = target
        opp_closer = cheb(ox, oy, tx, ty) <= cheb(sx, sy, tx, ty)
        if opp_closer:
            ds2_best = None
            target2 = None
            for rx, ry in resources:
                if cheb(sx, sy, rx, ry) < cheb(ox, oy, rx, ry):
                    ds2 = cheb(sx, sy, rx, ry)
                    if ds2_best is None or ds2 < ds2_best:
                        ds2_best = ds2
                        target2 = (rx, ry)
            if target2 is not None:
                tx, ty = target2
    else:
        tx, ty = w // 2, h // 2

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        score = -myd * 100 + opd
        if resources:
            if cheb(nx, ny, ox, oy) <= 1:
                score += 25
        else:
            score += -(cheb(nx, ny, w // 2, h // 2))
        if best is None or score > best[0]:
            best = (score, dx, dy)
    if best is None:
        return [0, 0]
    return [best[1], best[2]]