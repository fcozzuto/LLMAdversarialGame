def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("evade" in role) or ("runner" in role) or ("escape" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)
    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    if is_evader:
        tx = 0 if ox > (w - 1) / 2 else w - 1
        ty = 0 if oy > (h - 1) / 2 else h - 1
        target = (tx, ty)
        best = None
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_op = man(nx, ny, ox, oy)
            d_t = man(nx, ny, target[0], target[1])
            sc = d_op * 10 + d_t + mobility(nx, ny) * 0.1
            if sc > best_score:
                best_score, best = sc, (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]
    else:
        best = None
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_op = man(nx, ny, ox, oy)
            sc = -d_op * 10 + mobility(nx, ny) * 0.1
            if sc > best_score:
                best_score, best = sc, (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]