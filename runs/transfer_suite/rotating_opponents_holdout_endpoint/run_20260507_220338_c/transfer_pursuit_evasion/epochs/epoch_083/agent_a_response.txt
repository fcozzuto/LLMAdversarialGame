def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_evader = not any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx >= dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    near_corner = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**9)
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny)
        if i_am_evader:
            corner_bonus = -(abs(nx - far_corner[0]) + abs(ny - far_corner[1]))
            edge_pen = -10 * (1 if nx in (0, w - 1) or ny in (0, h - 1) else 0)
            val = d * 100 + corner_bonus + edge_pen - (abs(nx - near_corner[0]) + abs(ny - near_corner[1])) * 0.01
        else:
            corner_bonus = -(abs(nx - near_corner[0]) + abs(ny - near_corner[1]))
            edge_pen = -5 * (1 if nx in (0, w - 1) or ny in (0, h - 1) else 0)
            val = -d * 100 + corner_bonus + edge_pen
        if val > best[1]:
            best = ((dx, dy), val)
            best_move = [dx, dy]

    return best_move