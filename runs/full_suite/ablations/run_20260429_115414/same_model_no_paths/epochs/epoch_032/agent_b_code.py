def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        try:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
        except Exception:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if resources:
        opp_target = min(resources, key=lambda t: cheb(ox, oy, t[0], t[1]))
    else:
        opp_target = (ox, oy)

    oppd = cheb(ox, oy, opp_target[0], opp_target[1])

    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            myd = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        else:
            myd = cheb(nx, ny, ox, oy)
        my_to_opp = cheb(nx, ny, opp_target[0], opp_target[1])

        # Main: get to our nearest resource; Secondary: move to reduce opponent's access to their nearest target.
        val = (-myd) + 0.35 * (oppd - my_to_opp)

        # Small deterministic tie-break: prefer staying closer to center-ish and avoiding moving away from resources direction.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val -= 0.01 * cheb(nx, ny, int(cx), int(cy))

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]