def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_pursuer = any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx >= dy else dy

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    best_corner = corners[0]
    best_corner_dist = -1
    for c in corners:
        d = cheb(ox, oy, c[0], c[1])
        if d > best_corner_dist:
            best_corner_dist = d
            best_corner = c

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if i_am_pursuer:
            score = -cheb(nx, ny, ox, oy)
            # tiny tie-breaker: prefer moving toward the "most chased" corner of opponent position
            score += -0.01 * (cheb(ox, oy, best_corner[0], best_corner[1]))
        else:
            score = cheb(nx, ny, ox, oy)
            # steer toward farthest corner from opponent for wall-run behavior
            score += 0.01 * cheb(nx, ny, best_corner[0], best_corner[1])
        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], -t[1], -t[2]))
    return [int(candidates[-1][1]), int(candidates[-1][2])]