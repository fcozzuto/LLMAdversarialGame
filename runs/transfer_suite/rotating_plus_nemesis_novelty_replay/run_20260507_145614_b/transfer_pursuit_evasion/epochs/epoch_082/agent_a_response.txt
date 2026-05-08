def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("chaser" in self_role) or ("tag" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    obst_list = list(obst)

    def near_obstacle_pen(x, y):
        if (x, y) in obst:
            return 10**7
        if not obst_list:
            return 0.0
        best = 10**9
        for bx, by in obst_list:
            d = dist2(x, y, bx, by)
            if d < best:
                best = d
                if best == 0:
                    break
        if best == 10**9:
            return 0.0
        return 12.0 / (1.0 + best)

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) == (sx, sy) and (sx + dx < 0 or sx + dx >= w or sy + dy < 0 or sy + dy >= h):
            pass
        d = dist2(nx, ny, ox, oy)
        ppen = near_obstacle_pen(nx, ny)
        corner_bias = 0.0
        if not pursuer:
            # evader: also bias toward far corner when near an obstacle-heavy region
            corner_bias = 0.03 * max(abs(nx - 0) + abs(ny - 0), abs(nx - (w - 1)) + abs(ny - (h - 1)))
        if pursuer:
            val = d + 3.0 * ppen - 0.01 * corner_bias
        else:
            val = -d + 3.0 * ppen - 0.01 * corner_bias
        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]
    return [int(best[0]), int(best[1])]