def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    self_evader = ("evader" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def near_obst_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            xi = x + dx
            if xi < 0 or xi >= w: 
                continue
            for dy in (-1, 0, 1):
                yj = y + dy
                if yj < 0 or yj >= h:
                    continue
                if (xi, yj) in blocked:
                    pen += 2 if dx == 0 and dy == 0 else 1
        return pen

    # If you can capture immediately, prefer staying put (capture ends game; engine handles capture).
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_score = None

    # Deterministic tie-breaker: fixed iteration order in moves list.
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy  # engine keeps in place on invalid moves
        d = cheb(nx, ny, ox, oy)
        obst = near_obst_pen(nx, ny)
        # Small bias to avoid oscillations: prefer continuing in same general direction for pursuer,
        # and prefer reducing the chance of being cornered for evader.
        dir_bias = mdx * (ox - sx) + mdy * (oy - sy)
        stay_pen = 1 if (mdx == 0 and mdy == 0) else 0

        if self_evader:
            # maximize distance from pursuer, avoid obstacles
            score = d * 100 - obst * 3 - stay_pen * 2 + (dir_bias * -0.01)
        else:
            # minimize distance to evader, avoid obstacles
            score = -d * 100 - obst * 3 - stay_pen * 2 + (dir_bias * 0.01)

        if best_score is None or score > best_score:
            best_score = score
            best_m = (mdx, mdy)

    return [int(best_m[0]), int(best_m[1])]