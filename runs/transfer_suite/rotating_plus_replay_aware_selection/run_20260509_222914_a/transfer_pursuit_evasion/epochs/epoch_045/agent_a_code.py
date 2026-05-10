def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("evasion" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_pen(nx, ny):
        if (nx, ny) in obstacles:
            return 1e9
        if not obstacles:
            return 0.0
        dmin = 10**9
        for ax, ay in obstacles:
            d = abs(nx - ax) + abs(ny - ay)
            if d < dmin:
                dmin = d
        if dmin <= 0:
            return 1e9
        if dmin == 1:
            return 80.0
        if dmin == 2:
            return 20.0
        return 1.0 / (dmin + 1)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist = manh(nx, ny, ox, oy)

        # Evader: run to maximize distance and prefer moving toward farthest corner from pursuer.
        # Pursuer: chase to minimize distance and nudge toward center (avoid corner-lock pitfalls).
        if is_evader:
            far_corner = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
            corner_seek = manh(nx, ny, far_corner[0], far_corner[1])
            val = dist * 100.0 - corner_seek * 2.0
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            center_bias = -manh(nx, ny, cx, cy) * 0.5
            val = (-dist) * 100.0 + center_bias

        val -= obstacle_pen(nx, ny)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]