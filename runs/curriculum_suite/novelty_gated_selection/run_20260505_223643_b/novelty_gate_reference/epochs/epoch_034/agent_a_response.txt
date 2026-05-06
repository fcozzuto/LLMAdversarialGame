def choose_move(observation):
    def gi(v, d=0):
        try:
            return int(v)
        except:
            return d

    w = gi(observation.get("grid_width", 8), 8) or 8
    h = gi(observation.get("grid_height", 8), 8) or 8
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = gi(sp[0], 0), gi(sp[1], 0)
    ox, oy = gi(op[0], 0), gi(op[1], 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = gi(p[0], 0), gi(p[1], 0)
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    targets = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        x, y = gi(r[0], 0), gi(r[1], 0)
        if inside(x, y) and (x, y) not in obs:
            targets.append((x, y))

    if targets:
        tx, ty = min(targets, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0] + t[1], t[0], t[1]))
        tx2, ty2 = ox, oy
        intercept_weight = 2 if cheb(sx, sy, ox, oy) <= 2 else 0
    else:
        tx, ty = ox, oy
        tx2, ty2 = ox, oy
        intercept_weight = 0

    move_list = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**9)
    for dx, dy in move_list:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        d1 = cheb(nx, ny, tx, ty)
        d0 = cheb(sx, sy, tx, ty)
        gain_res = (d0 - d1)
        dop1 = cheb(nx, ny, ox, oy)
        dop0 = cheb(sx, sy, ox, oy)
        gain_int = (dop0 - dop1)
        on_res = 1 if targets and (nx, ny) in targets else 0
        score = 6 * gain_res + intercept_weight * 4 * gain_int + on_res * 20 - (1 if (nx, ny) == (sx, sy) else 0)
        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    dx, dy = best[0]
    return [int(dx), int(dy)]