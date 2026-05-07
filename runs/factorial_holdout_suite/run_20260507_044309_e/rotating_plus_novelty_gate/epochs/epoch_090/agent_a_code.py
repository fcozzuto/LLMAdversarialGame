def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    if res_list:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in res_set:
                return [dx, dy]
            sd = 10**9
            adv_best = -10**9
            for rx, ry in res_list:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                if d_self < sd:
                    sd = d_self
                adv = d_opp - d_self
                if adv > adv_best:
                    adv_best = adv
            cand = (adv_best, -sd, dx, dy)
            if best is None or cand > best:
                best = cand
        if best is not None:
            return [best[2], best[3]]

    # No resources (or all moves blocked): move to improve distance to opponent corner
    # Deterministic: step that minimizes cheb distance to opponent.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        cand = (-d, dx, dy)
        if best is None or cand > best:
            best = cand
    return [best[1], best[2]] if best is not None else [0, 0]