def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    mode_away = ("evader" in self_role) or ("runner" in self_role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def open_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if mode_away:
        # Steer toward the farthest corner from opponent, but keep distance
        target_corner = max(corners, key=lambda t: manh(t[0], t[1], ox, oy))
        base_sign = 1
    else:
        # Chase by pushing toward the nearest corner from opponent (more forcing), but mainly reduce distance
        target_corner = min(corners, key=lambda t: manh(t[0], t[1], ox, oy))
        base_sign = -1

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        dist = manh(nx, ny, ox, oy)
        corner_dist = manh(nx, ny, target_corner[0], target_corner[1])
        opp_corner = min(corners, key=lambda t: manh(ox, oy, t[0], t[1])) if not mode_away else min(corners, key=lambda t: manh(ox, oy, t[0], t[1]))
        opp_threat = manh(ox, oy, opp_corner[0], opp_corner[1])

        mobility = open_neighbors(nx, ny)

        # Deterministic composite score: away maximizes dist and mobility; chase minimizes dist and corner_dist
        v = base_sign * (dist * 10.0 + corner_dist * 1.2) + (mobility * (2.0 if mode_away else 0.3))
        # Small tie-breaker prefers diagonal progress deterministically
        v += (dx * 0.01 + dy * 0.005)

        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]