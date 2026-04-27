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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_r = None
        best_s = -10**9
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources we're closer to; slight bias toward nearer overall and not directly behind opponent.
            s = (d_opp - d_self) * 100 + (-d_self) * 2 + (rx + ry) * 0.01 - cheb(ox, oy, sx, sy) * 0.001
            if s > best_s:
                best_s = s
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # No visible resources: drift toward center.
        tx, ty = (w // 2, h // 2)

    best_move = [0, 0]
    best_val = -10**9
    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            # invalid moves just keep position, emulate that deterministically
            nx, ny = sx, sy
        d_self = cheb(nx, ny, tx, ty)
        d_opp_after = cheb(ox, oy, tx, ty)
        # maximize reduction in our distance to target; if similar, maximize our safety vs opponent by distancing from them.
        dist_opp_here = cheb(nx, ny, ox, oy)
        val = (-d_self) * 100 + (d_self == 0) * 100000 + dist_opp_here * 1 - d_opp_after * 0.01
        if val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]