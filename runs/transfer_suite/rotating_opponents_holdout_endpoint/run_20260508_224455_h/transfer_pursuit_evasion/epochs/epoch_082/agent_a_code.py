def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    sr = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in sr) or ("hunter" in sr)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # obstacle proximity penalty
    def obst_pen(x, y):
        p = 0
        for ex, ey in obs:
            dx, dy = x - ex, y - ey
            d2 = dx * dx + dy * dy
            if d2 == 0:
                return 10**9
            if d2 <= 9:  # within 3 steps (Chebyshev-ish)
                p += (9 - d2)
        return p

    # evader "wall-run" bias: prefer getting farther from pursuer while aligning to far corner
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    cx, cy = far_corner

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        ppen = obst_pen(nx, ny)

        # additional alignment term to reduce "bouncing" near obstacles
        align = -dist2(nx, ny, cx, cy)  # negative: larger is worse for evader, better for pursuer to avoid it
        # pursuer wants to move toward opponent; evader wants to move away and toward far corner
        if is_pursuer:
            val = d2 + 0.7 * ppen + 0.02 * (-align)  # slightly avoid far corner to cut evader's path
        else:
            val = -d2 + 0.85 * ppen + 0.03 * align  # maximize d2 => minimize -d2; plus corner alignment

        if best is None or val < best:
            best = val
            best_move = [dx, dy]

    return best_move