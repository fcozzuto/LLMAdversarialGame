def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    evading = ("evader" in role) or ("runner" in role)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        return abs(ax - bx) if abs(ax - bx) > abs(ay - by) else abs(ay - by)

    def obst_near(x, y):
        m = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if (x + i, y + j) in blocked:
                    m += 1
        return m

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d = cheb(nx, ny, ox, oy)
        far_corner = max(cheb(nx, ny, cx, cy) for cx, cy in corners)
        near_ob = obst_near(nx, ny)

        # One-step "danger": assume opponent moves to reduce (if it's pursuer) or increase (if it's evader).
        opp_role = str(observation.get("opponent_role", "")).lower()
        opp_evading = ("evader" in opp_role) or ("runner" in opp_role)
        opp_best = None
        for odx, ody in moves:
            px, py = ox + odx, oy + ody
            if not inb(px, py) or (px, py) in blocked:
                continue
            dd = cheb(nx, ny, px, py)
            val = dd if opp_evading else -dd
            if opp_best is None or val > opp_best:
                opp_best = val
        d_pred = -opp_best if not opp_evading else opp_best

        # Score: pursuer wants smaller distance; evader wants larger.
        if evading:
            val = (2.2 * d) + (1.0 * far_corner) - (0.6 * near_ob) + (1.0 * d_pred)
        else:
            val = (-2.2 * d) + (0.2 * far_corner) - (0.8 * near_ob) + (-1.0 * d_pred)

        if best_val is None or (val > best_val):
            best_val = val
            best_move = [dx, dy]

    return best_move