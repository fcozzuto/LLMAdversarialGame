def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opp_role and "pursuer" not in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_corner_dist(x, y):
        bc = -1
        for cx, cy in corners:
            d = cheb(x, y, cx, cy)
            if d > bc:
                bc = d
        return bc

    if is_evader:
        # Run from pursuer while drifting toward the farthest corner.
        far_corner = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), -c[0], -c[1]))
        best = None
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, far_corner[0], far_corner[1])
            center_push = -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)
            # Prefer increasing escape distance; slightly prefer corner drift and staying deterministic.
            val = d_opp * 1000 + d_corner * 10 + center_push
            if val > best_val:
                best_val = val
                best = [dx, dy]
        return best if best is not None else [0, 0]
    else:
        # Chase pursuer role: move to reduce distance to evader (obstacle-aware greedy).
        best = None
        best_val = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            # Encourage direct progress and avoid dithering.
            jitter = 0 if (dx == 0 and dy == 0) else 1
            val = d_opp * 1000 - jitter
            if val < best_val:
                best_val = val
                best = [dx, dy]
        return best if best is not None else [0, 0]