def choose_move(observation):
    def to_int(v, d=0):
        try:
            return int(v)
        except:
            return d

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = to_int(sx), to_int(sy), to_int(ox), to_int(oy)

    w = to_int(observation.get("grid_width", 8), 8) or 8
    h = to_int(observation.get("grid_height", 8), 8) or 8

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = to_int(p[0]), to_int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def obstacle_penalty(x, y):
        # discourage moving adjacent to obstacles (simple local safety)
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in obs:
                    p += 1
        return p

    # If no resources, drift to center and away from obstacles.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy, nx, ny in legal:
            score = dist_cheb(nx, ny, cx, cy) + 0.25 * obstacle_penalty(nx, ny)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Choose the move that maximizes our advantage for reaching a contested resource.
    best = None
    for dx, dy, nx, ny in legal:
        # Our best target from this next position: minimize (our distance - 0.9*opponent advantage)
        best_target = None
        for rx, ry in resources:
            ds = dist_cheb(nx, ny, rx, ry)
            do = dist_cheb(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer than opponent.
            # Also slightly discourage long detours.
            obj = ds - 0.9 * do + 0.05 * (ds * ds)
            if best_target is None or obj < best_target:
                best_target = obj
        # Small tie-break: push away from obstacles and keep some directionality.
        center_bias = dist_cheb(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0) * 0.02
        score = best_target + 0.35 * obstacle_penalty(nx, ny) + center_bias
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]