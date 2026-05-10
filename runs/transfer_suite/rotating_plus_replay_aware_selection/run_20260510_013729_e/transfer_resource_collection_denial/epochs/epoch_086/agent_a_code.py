def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst_list = observation.get("obstacles") or []
    obst = set()
    for p in obst_list:
        try:
            x, y = p
            obst.add((int(x), int(y)))
        except Exception:
            pass
    resources = observation.get("resources") or []
    res = []
    for p in resources:
        try:
            x, y = p
            res.append((int(x), int(y)))
        except Exception:
            if isinstance(p, dict) and "position" in p:
                x, y = p["position"]
                res.append((int(x), int(y)))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def legal(x, y):
        return inb(x, y) and (x, y) not in obst
    def man(ax, ay, bx, by):
        ax -= bx
        if ax < 0: ax = -ax
        ay -= by
        if ay < 0: ay = -ay
        return ax + ay
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    if res:
        tx, ty = min(res, key=lambda r: man(sx, sy, r[0], r[1]))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_self = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ox, oy)
            key = (d_self, -d_opp, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_opp = man(nx, ny, ox, oy)
            key = (-d_opp, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]