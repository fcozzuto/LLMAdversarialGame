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
            obstacles.add((int(p[0]), int(p[1])))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        m = dx if dx >= dy else dy
        return m * m

    def center_score(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = x - cx
        dy = y - cy
        return -(dx * dx + dy * dy)

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d2 = cheb2(nx, ny, ox, oy)
        c2 = center_score(nx, ny)

        # deterministic obstacle avoidance: slight penalty for being adjacent to many obstacles
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    adj += 1

        if is_evader:
            # maximize distance; prefer safer (less-adjacent) and then prefer toward center slightly (prevents corners trapping)
            key = (d2, -adj, c2, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        else:
            # pursuer: minimize distance; prefer safer and toward center
            key = (-d2, -adj, c2, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]