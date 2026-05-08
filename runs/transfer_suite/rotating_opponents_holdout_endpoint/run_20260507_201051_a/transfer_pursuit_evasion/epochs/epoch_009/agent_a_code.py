def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    if w <= 0 or h <= 0:
        w, h = 8, 8

    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    self_role = observation.get("self_role", "pursuer")
    is_evader = (str(self_role).lower() == "evader")
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    if is_evader:
        # Run to the corner farthest from pursuer, avoid obstacles by choosing best adjacent move.
        target = None
        best = None
        for cx, cy in corners:
            if not free(cx, cy):
                continue
            d = cheb(ox, oy, cx, cy)
            if best is None or d > best or (d == best and (cx, cy) < target):
                best, target = d, (cx, cy)
        if target is None:
            target = (0, 0)
        tx, ty = target

        best_move = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # Prefer increasing distance to pursuer; tie-break by closer to target to reach safety.
            score = (cheb(ox, oy, nx, ny), -cheb(nx, ny, tx, ty))
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)
        return [best_move[0], best_move[1]]

    # Pursuer: minimize distance to evader; when evader is near a corner, prioritize cutting it off.
    ev_corner = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # Intercept heuristic: move to squares that reduce distance while also aligning with evader->our direction.
        align = abs(nx - ox) + abs(ny - oy)
        # If evader is in/near a corner, slightly prefer increasing coverage (moving toward the nearer boundary).
        boundary_bias = 0
        if ev_corner:
            bx = 0 if ox <= w // 2 else w - 1
            by = 0 if oy <= h // 2 else h - 1
            boundary_bias = -cheb(nx, ny, bx, by)
        score = (-d, -align, boundary_bias)
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)
    return [best_move[0], best_move[1]]