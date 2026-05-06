def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if is_free(nx, ny):
                    return [dx, dy]
        return [0, 0]

    best = None
    best_key = None
    for x, y in resources:
        self_d = md(sx, sy, x, y)
        opp_d = md(ox, oy, x, y)
        slack = opp_d - self_d
        if best_key is None or (self_d <= opp_d + 1 and (slack, -self_d, x, y) > best_key):
            best = (x, y)
            best_key = (slack, -self_d, x, y)

    if best is None:
        for x, y in resources:
            self_d = md(sx, sy, x, y)
            opp_d = md(ox, oy, x, y)
            key = (opp_d - self_d, -self_d, x, y)
            if best_key is None or key > best_key:
                best = (x, y)
                best_key = key

    tx, ty = best
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if is_free(nx, ny):
                moves.append((dx, dy, nx, ny))

    cur_d = md(sx, sy, tx, ty)
    best_m = None
    best_m_key = None
    for dx, dy, nx, ny in moves:
        nd = md(nx, ny, tx, ty)
        # Prefer progress; if tied, prefer getting closer relative to opponent.
        opp_nd = md(ox, oy, tx, ty)
        key = (-(nd), -(nd - opp_nd), -abs(nx - tx) - abs(ny - ty), dx, dy)
        # Primary progress vs current distance
        key = (-(nd), nd <= cur_d, -(nd - (cur_d)), -(abs(nx - tx) + abs(ny - ty)), dx, dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]