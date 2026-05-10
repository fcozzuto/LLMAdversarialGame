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

    def obst_pen(nx, ny):
        p = 0
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d == 0: return 10**6
            if d == 1: p += 5
            elif d == 2: p += 2
        return p

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        tx, ty = target

        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            # Prefer increasing distance from pursuer; also drift toward farthest corner from pursuer.
            score = 3 * cheb(nx, ny, ox, oy) + 1.2 * (-cheb(nx, ny, tx, ty)) - obst_pen(nx, ny)
            if best_score is None or score > best_score:
                best_score, best = score, [dx, dy]
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Prefer decreasing distance to opponent; lightly penalize obstacles.
            score = -3 * cheb(nx, ny, ox, oy) - 0.8 * obst_pen(nx, ny)
            if best_score is None or score > best_score:
                best_score, best = score, [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]