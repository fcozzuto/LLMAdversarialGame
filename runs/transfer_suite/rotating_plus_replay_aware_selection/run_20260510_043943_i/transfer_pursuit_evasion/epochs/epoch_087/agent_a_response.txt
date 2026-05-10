def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        target = (ox, oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def obstacle_penalty(nx, ny):
        if not obstacles:
            return 0
        pen = 0
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d == 0:
                return 10**6
            if d == 1:
                pen += 7
            elif d == 2:
                pen += 2
        return pen

    best = None
    best_score = None
    # Deterministic tie-breaker: fixed dir order; keep first best.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, target[0], target[1])
        # Pursuer: minimize distance; Evader: maximize distance.
        base = d if not is_evader else -d
        pen = obstacle_penalty(nx, ny)
        # Slight bias toward staying centered (deterministic, prevents oscillation).
        center_bias = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
        score = base + pen + (0.05 * center_bias)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]