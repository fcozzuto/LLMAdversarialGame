def choose_move(observation):
    def ti(v, d=0):
        try:
            return int(v)
        except:
            return d

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = ti(sx), ti(sy), ti(ox), ti(oy)
    w = ti(observation.get("grid_width", 8), 8) or 8
    h = ti(observation.get("grid_height", 8), 8) or 8

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = ti(p[0]), ti(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def near_obstacle(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    return 1
        return 0

    # Pick a target deterministically: prefer resources we can beat the opponent to.
    best = None
    best_key = None
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = ti(r[0]), ti(r[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        d_us = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # key: maximize urgency (opponent advantage we can steal), then minimize our distance
        steal = d_op - d_us  # positive if we are closer
        key = (-1 if steal <= 0 else 0, -steal, d_us, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Score each legal move; avoid obstacles and try to reduce distance to target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # Slightly prefer moving away from opponent while advancing target (interceptor feel).
        score = d * 10 + near_obstacle(nx, ny) * 7 - (1 if d_op >= 1 else 0) - (1 if (ox, oy) == (nx, ny) else 0)
        # Deterministic tie-break by move ordering
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]