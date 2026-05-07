def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def best_target_value(px, py):
        best = None
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            # counter "sweep_rows": favor targets in rows that reduce their relative progress
            row_delta = abs(ry - oy)
            # prefer grabbing something sooner when advantage is similar
            key = (adv, -sd, row_delta, -((ry - oy) & 1))
            if best is None or key > best:
                best = key
        return best

    best_move = [0, 0]
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = best_target_value(nx, ny)
            if val is None:
                continue
            # primary: maximize advantage; secondary: reach sooner; tertiary: row control
            key = val
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]

    if best_key is None:
        # fallback: go toward nearest resource
        tr = resources[0]
        td = cheb(sx, sy, tr[0], tr[1])
        for rx, ry in resources[1:]:
            d = cheb(sx, sy, rx, ry)
            if d < td:
                td = d
                tr = (rx, ry)
        tx, ty = tr
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy):
            return [dx, dy]
        # try axis steps deterministically
        if inb(sx + dx, sy):
            return [dx, 0]
        if inb(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    return best_move