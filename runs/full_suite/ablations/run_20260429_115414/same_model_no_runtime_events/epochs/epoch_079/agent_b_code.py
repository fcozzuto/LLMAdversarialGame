def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            d = dist(sx, sy, rx, ry)
            if best is None or d < best:
                best = d
                target = (rx, ry)
    else:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        bestd = -1
        for cx, cy in corners:
            d = dist(cx, cy, ox, oy)
            if d > bestd:
                bestd = d
                target = (cx, cy)

    tx, ty = target
    best_move = (0, 0)
    best_score = None
    pref = [0, -1, 1, -0.1]  # tie-breaker order hint
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = dist(nx, ny, tx, ty)
        # Slightly discourage moving closer to opponent when no resources
        if not resources:
            score = score - 0.01 * dist(nx, ny, ox, oy)
        if best_score is None or score < best_score or (score == best_score and i < pref[1] + 100):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]