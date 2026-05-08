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

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("tag" in role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def near_obst_pen(x, y):
        if (x, y) in obst:
            return 10**8
        best = 10**9
        for bx, by in obst:
            d = (x - bx) * (x - bx) + (y - by) * (y - by)
            if d < best:
                best = d
        if best == 10**9:
            return 0
        return 10.0 / (1.0 + best)

    best_move = (0, 0)
    best_val = None

    if not is_pursuer:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        targ = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            val = -10**18 if is_pursuer else -10**18
        else:
            d_op = dist2(nx, ny, ox, oy)
            pen = near_obst_pen(nx, ny)
            if is_pursuer:
                # maximize approach (smaller distance), strongly avoid near obstacles
                val = (-d_op) - 2.5 * pen - 0.001 * (dx * dx + dy * dy)
            else:
                # maximize escape and head toward the corner farthest from pursuer
                d_t = dist2(nx, ny, targ[0], targ[1])
                val = d_op + 0.35 * d_t - 2.5 * pen - 0.001 * (dx * dx + dy * dy)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]