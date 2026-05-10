def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = observation.get("self_role", "pursuer")
    is_pursuer = (role == "pursuer")  # otherwise evader

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def step_ok(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h):
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    # Preferred direction toward/away from opponent based on sign, with deterministic tie-break
    dx_dir = 0 if ox == sx else (1 if ox > sx else -1)
    dy_dir = 0 if oy == sy else (1 if oy > sy else -1)
    if not is_pursuer:
        dx_dir, dy_dir = -dx_dir, -dy_dir

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        # Greedy objective: pursue = minimize dist, evade = maximize dist
        d = dist2(nx, ny, ox, oy)
        obj = d if not is_pursuer else -d  # higher is better
        # Obstacle proximity penalty (local)
        penalty = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    penalty += 1
        # Directional bias and small preference for staying if tied
        dir_bias = 1 if (dx == dx_dir) else 0
        dir_bias += 1 if (dy == dy_dir) else 0
        stay_bias = 1 if (dx == 0 and dy == 0) else 0

        score = obj + 0.15 * dir_bias - 0.25 * penalty + 0.01 * stay_bias
        key = (score, -abs(nx - clamp(nx, 0, w - 1)) - abs(ny - clamp(ny, 0, h - 1)))
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]